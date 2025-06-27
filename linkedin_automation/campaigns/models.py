from django.db import models
from django.contrib.auth.models import User



class Campaign(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        default='Pending',
        choices=[
            ('Pending', 'Pending'),
            ('Running', 'Running'),
            ('Completed', 'Completed')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.domain} - {self.owner.username}"


class Profile(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    url = models.URLField()
    status = models.CharField(
        max_length=50,
        default='Pending',
        choices=[
            ('Pending', 'Pending'),
            ('Sent', 'Sent'),
            ('Accepted', 'Accepted'),
            ('Failed', 'Failed')
        ]
    )

    def __str__(self):
        return self.url