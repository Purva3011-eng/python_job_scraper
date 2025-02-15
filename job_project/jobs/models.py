from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)

    def __str__(self):
        return self.title
