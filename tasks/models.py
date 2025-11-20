from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
	name = models.CharField(max_length=200)

	class Meta:
		verbose_name_plural = 'categories'

	def __str__(self):
		return self.name


class Task(models.Model):
	title = models.CharField(max_length=100)
	due_date = models.DateField(null=True, blank=True)
	is_completed = models.BooleanField(default=False)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')

	class Meta:
		# Order tasks by due date (earliest first). Adjust as needed.
		ordering = ['due_date']

	def save(self, *args, **kwargs):
		if len(self.title) > 100:
			raise ValidationError("Title cannot be longer than 100 characters")
		super().save(*args, **kwargs)
	
	def __str__(self):
		return self.title
