from django.test import TestCase, Client
from django.urls import reverse


class TaskViewsTest(TestCase):
    def setUp(self):
        # Import models here so running file directly works
        from tasks.models import Task, Category
        from django.conf import settings

        # allow testserver host when running this file directly
        try:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
        except Exception:
            pass

        # When running this file directly (not via manage.py test) the
        # CSRF middleware can cause 403 responses for test client POSTs.
        # Remove CsrfViewMiddleware from settings.MIDDLEWARE if present so
        # the direct-run test client can exercise view logic the same way
        # as the Django test runner does.
        try:
            mw = list(settings.MIDDLEWARE)
            csrf_path = 'django.middleware.csrf.CsrfViewMiddleware'
            if csrf_path in mw:
                mw.remove(csrf_path)
                settings.MIDDLEWARE = mw
        except Exception:
            pass
        self.client = Client()
        self.cat = Category.objects.create(name='QuickTest')
        Task.objects.create(title='Quick task', category=self.cat)

        from tasks.forms import TaskForm

        self.Task = Task
        self.Category = Category
        self.TaskForm = TaskForm

        self.pending = Task.objects.create(title='Pending', category=self.cat, is_completed=False)
        self.completed = Task.objects.create(title='Done', category=self.cat, is_completed=True)

    def test_index_view_get_and_context(self):
        """GET / should return 200, use index template, and include expected context."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Template
        self.assertTemplateUsed(response, 'tasks/index.html')
        # Context keys
        self.assertIn('form', response.context)
        self.assertIn('upcoming_tasks', response.context)
        self.assertIn('completed_tasks', response.context)
        # The pending/completed tasks should appear in their respective lists
        upcoming_pks = [t.pk for t in response.context['upcoming_tasks']]
        completed_pks = [t.pk for t in response.context['completed_tasks']]
        self.assertIn(self.pending.pk, upcoming_pks)
        self.assertIn(self.completed.pk, completed_pks)

    def test_create_task_via_post_valid(self):
        """POST with valid data should create a Task and redirect to index."""
        data = {
            'title': 'Newly posted task',
            'due_date': '',
            'category': str(self.cat.pk),
        }
        response = self.client.post(reverse('index'), data)
        # view redirects on success
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.Task.objects.filter(title='Newly posted task').exists())

    def test_create_task_via_post_invalid(self):
        """POST with invalid data (missing title) should re-render form with errors."""
        data = {
            'title': '',
            'due_date': '',
            'category': str(self.cat.pk),
        }
        response = self.client.post(reverse('index'), data)
        # Should return 200 and not create the object
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.Task.objects.filter(title='').exists())
        # Form errors should be present in context
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

    def test_index_view_get(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_mark_complete_view(self):
        """POSTing to complete should mark a pending task as completed."""
        url = reverse('task-complete', args=[self.pending.pk])
        response = self.client.post(url)
        # should redirect
        self.assertEqual(response.status_code, 302)
        self.pending.refresh_from_db()
        self.assertTrue(self.pending.is_completed)

    def test_reopen_task_view(self):
        """POSTing to reopen should mark a completed task as not completed."""
        url = reverse('task-reopen', args=[self.completed.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.completed.refresh_from_db()
        self.assertFalse(self.completed.is_completed)

    def test_delete_task_view(self):
        """POSTing to delete should remove the task from the DB."""
        # create a task to delete
        t = self.Task.objects.create(title='To be deleted', category=self.cat)
        url = reverse('task-delete', args=[t.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.Task.objects.filter(pk=t.pk).exists())

    def test_edit_task_view_get_and_post(self):
        """GET shows the edit form; POST updates the task."""
        # GET
        url = reverse('task-edit', args=[self.pending.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # POST update title
        data = {'title': 'Updated Pending', 'due_date': '', 'category': str(self.cat.pk)}
        post = self.client.post(url, data)
        self.assertEqual(post.status_code, 302)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.title, 'Updated Pending')

    # Edge-case / robustness tests
    def test_create_with_invalid_category_id(self):
        """POSTing with a non-existent category id should not create a Task and should show form errors."""
        data = {'title': 'Bad Category', 'due_date': '', 'category': '99999'}
        response = self.client.post(reverse('index'), data)
        self.assertEqual(response.status_code, 200)
        # Form should be present and have errors for 'category'
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        # Ensure no task was created with that title
        self.assertFalse(self.Task.objects.filter(title='Bad Category').exists())

    def test_mark_complete_on_already_completed(self):
        """Calling mark_complete on an already completed task should be a no-op and still redirect."""
        # ensure completed
        self.completed.is_completed = True
        self.completed.save()
        url = reverse('task-complete', args=[self.completed.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.completed.refresh_from_db()
        self.assertTrue(self.completed.is_completed)

    def test_reopen_on_pending_task(self):
        """Calling reopen on a pending task should leave it pending and redirect."""
        url = reverse('task-reopen', args=[self.pending.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.pending.refresh_from_db()
        self.assertFalse(self.pending.is_completed)

    def test_delete_nonexistent_task_returns_404(self):
        """Posting to delete a non-existent PK should return 404."""
        url = reverse('task-delete', args=[999999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_invalid_post_shows_errors(self):
        """Submitting invalid data to edit view should re-render the form with errors and not change the task."""
        url = reverse('task-edit', args=[self.pending.pk])
        old_title = self.pending.title
        data = {'title': '', 'due_date': '', 'category': str(self.cat.pk)}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        form = resp.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.title, old_title)


if __name__ == '__main__':
    import os
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')
    import django
    django.setup()

    # Prefer running tests via Django's test runner to ensure correct DB
    # setup and middleware behavior when executing this file directly.
    from django.conf import settings
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(['tasks.test_views'])
    sys.exit(bool(failures))
