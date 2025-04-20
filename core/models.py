from django.db import models
from django.contrib.auth.models import User


# TODO : [The id field is marked as serialize=False so we need to take care of this later]
class Resturant(models.Model):
    class CusineType(models.TextChoices):
        INDIAN = 'IN', 'Indian'
        ITALIAN = 'IT', 'Italian'
        CHINESE = 'CH', 'Chinese'
        MEXICAN = 'MX', 'Mexican'
        AMERICAN = 'AM', 'American'

    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    opened_at = models.DateField()
    website = models.URLField(default="")
    causine = models.CharField(
        max_length=2, choices=CusineType.choices, default=CusineType.AMERICAN)

    def __str__(self):
        return self.name


class Rating(models.Model):
    stars = models.PositiveSmallIntegerField()
    comment = models.TextField()
    resturant = models.ForeignKey(
        Resturant, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return f"{self.user.username} - {self.resturant.name} - {self.stars} stars"


class Sale(models.Model):
    resturant = models.ForeignKey(
        Resturant, on_delete=models.CASCADE, related_name='sales')
    saled_at = models.DateTimeField()
    income = models.DecimalField(max_digits=10, decimal_places=2)
