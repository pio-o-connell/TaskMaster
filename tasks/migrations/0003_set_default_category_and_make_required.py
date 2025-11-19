from django.db import migrations, models


def set_default_category(apps, schema_editor):
    Category = apps.get_model('tasks', 'Category')
    Task = apps.get_model('tasks', 'Task')
    cat, _ = Category.objects.get_or_create(name='Uncategorized')
    Task.objects.filter(category__isnull=True).update(category=cat)


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_category_alter_task_options_and_more'),
    ]

    operations = [
        migrations.RunPython(set_default_category, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tasks', to='tasks.Category'),
        ),
    ]
