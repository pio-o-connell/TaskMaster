from django.test import TestCase


class TaskFormTest(TestCase):
    """Tests for `TaskForm` validating valid/invalid and edge-case inputs."""

    def setUp(self):
        # Defer imports so the module can be executed directly
        from tasks.forms import TaskForm
        from tasks.models import Category, Task
        from django.core.exceptions import ValidationError

        self.TaskForm = TaskForm
        self.Task = Task
        self.Category = Category
        self.ValidationError = ValidationError

        # fixtures
        self.cat = Category.objects.create(name='FormCategory')

        # baseline valid payload
        self.valid_data = {
            'title': 'A valid task',
            'due_date': '',
            'category': str(self.cat.pk),
        }

        # invalid/edge payloads
        self.invalid_category_data = {
            'title': 'Bad category',
            'due_date': '',
            'category': '99999',
        }

        max_len = self.Task._meta.get_field('title').max_length
        self.max_len = max_len
        self.too_long_title = 'T' * (max_len + 1)
        self.too_long_data = {
            'title': self.too_long_title,
            'due_date': '',
            'category': str(self.cat.pk),
        }

    def test_form_valid_data_is_valid(self):
        form = self.TaskForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form should be valid, errors: {form.errors}")

    def test_form_with_invalid_category_shows_errors(self):
        form = self.TaskForm(data=self.invalid_category_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_form_with_missing_title_is_invalid(self):
        data = self.valid_data.copy()
        data['title'] = ''
        form = self.TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_with_missing_category_is_invalid(self):
        data = self.valid_data.copy()
        data.pop('category')
        form = self.TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_form_title_too_long_rejected_by_form_validation(self):
        form = self.TaskForm(data=self.too_long_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_model_full_clean_rejects_too_long_title(self):
        t = self.Task(title=self.too_long_title, category=self.cat)
        with self.assertRaises(self.ValidationError):
            t.full_clean()

    def test_boundary_title_length_accepts_max_length(self):
        title = 'T' * self.max_len
        data = self.valid_data.copy()
        data['title'] = title
        form = self.TaskForm(data=data)
        self.assertTrue(form.is_valid(), f"Boundary title should be valid; errors: {form.errors}")
        # also ensure model full_clean accepts it
        t = self.Task(title=title, category=self.cat)
        try:
            t.full_clean()
        except Exception as exc:
            self.fail(f"Model full_clean() raised unexpectedly for boundary title: {exc}")


if __name__ == '__main__':
    # Run tests using Django's test runner so DB/middleware are configured
    import os
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')
    import django
    django.setup()

    from django.conf import settings
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(['tasks.test_forms'])
    sys.exit(bool(failures))
