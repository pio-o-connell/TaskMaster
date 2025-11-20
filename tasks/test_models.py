from django.test import TestCase
import datetime
# NOTE: do not import `tasks.models` at module import time — defer inside setUp


class TaskModelTest(TestCase):
    """Test skeleton for the Task model (tests not implemented)."""


    def setUp(self):
        # Fixtures for tests
        # import models here so running this module directly works (we set up
        # sys.path and DJANGO_SETTINGS_MODULE in the __main__ block below)
        from tasks.models import Task, Category

        self.category = Category.objects.create(name='Test Category')
        self.task = Task.objects.create(
            title='Test Task',
            is_completed=False,
            category=self.category,
        )
        self.task_with_due = Task.objects.create(
            title='Due Task',
            due_date=datetime.date.today(),
            is_completed=False,
            category=self.category,
        )



    def test_task_creation(self):
        # Verify the fixtures created in setUp
        self.assertIsNotNone(self.task.pk, "Task created in setUp should have a primary key")
        self.assertEqual(self.task.title, 'Test Task')
        self.assertFalse(self.task.is_completed)
        self.assertEqual(self.task.category.name, 'Test Category')

        # The task with due date should have today's date
        self.assertIsNotNone(self.task_with_due.pk, "Task with due date should have a primary key")
        self.assertEqual(self.task_with_due.due_date, datetime.date.today())

    def test_str_returns_title(self):
        # str(task) should return the task title
        self.assertEqual(str(self.task), self.task.title)

    def test_default_is_completed_false(self):
        # Newly created Task should have is_completed == False by default
        from tasks.models import Task

        new_task = Task.objects.create(title='Default Flag Task', category=self.category)
        self.assertFalse(new_task.is_completed)

    def test_due_date_can_be_null(self):
        # Creating a Task without a due_date should be allowed (null/blank)
        from tasks.models import Task

        no_due = Task.objects.create(title='No Due', category=self.category, due_date=None)
        self.assertIsNone(no_due.due_date)

    def test_category_relation(self):
        # Category relation: task.category should be a Category and reverse lookup should work
        from tasks.models import Category, Task

        self.assertIsInstance(self.task.category, Category)
        # Ensure the category assigned in setUp matches
        self.assertEqual(self.task.category.pk, self.category.pk)

        # Reverse lookup: tasks for this category should include our task
        tasks_for_category = Task.objects.filter(category=self.category)
        self.assertIn(self.task, list(tasks_for_category))

    def test_task_ordering_if_defined(self):
        # If Task.Meta.ordering is defined, assert that queryset respects it.
        from tasks.models import Task
        ordering = getattr(Task._meta, 'ordering', None)
        if not ordering:
            self.skipTest('Task.Meta.ordering is not defined')

        # Create tasks with different titles/due_dates to test ordering
        Task.objects.all().delete()
        t1 = Task.objects.create(title='A Task', due_date=datetime.date(2025, 1, 2), category=self.category)
        t2 = Task.objects.create(title='B Task', due_date=datetime.date(2025, 1, 1), category=self.category)
        t3 = Task.objects.create(title='C Task', due_date=datetime.date(2025, 1, 3), category=self.category)

        qs = list(Task.objects.all())

        # Build a key function to compare against ordering tuple
        def key_for(task):
            vals = []
            for field in ordering:
                if field.startswith('-'):
                    fname = field[1:]
                    rev = True
                else:
                    fname = field
                    rev = False
                val = getattr(task, fname)
                vals.append((val, rev))
            return vals

        # Ensure the queryset is sorted according to the meta ordering
        sorted_qs = sorted(qs, key=lambda t: tuple((getattr(t, f.lstrip('-')) if not f.startswith('-') else getattr(t, f.lstrip('-')) for f in ordering)))
        self.assertEqual(qs, sorted_qs)


    def test_title_max_length(self):
        # CharField enforces max_length during validation (full_clean()) not on save.
        from django.core.exceptions import ValidationError
        from tasks.models import Task

        max_len = Task._meta.get_field('title').max_length
        long_title = 'T' * (max_len + 1)
        task = Task(title=long_title, category=self.category)
        with self.assertRaises(ValidationError):
            task.full_clean()

            
if __name__ == '__main__':
    # Allow running this test module directly for quick feedback.
    # Ensure project root is on sys.path and Django is configured.
    import os
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')
    import django
    django.setup()

    import unittest
    unittest.main()