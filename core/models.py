from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# TODO : [The id field is marked as serialize=False so we need to take care of this later]


class Resturant(models.Model):
    class CusineType(models.TextChoices):
        INDIAN = 'IN', 'Indian'
        ITALIAN = 'IT', 'Italian'
        CHINESE = 'CH', 'Chinese'
        MEXICAN = 'MX', 'Mexican'
        AMERICAN = 'AM', 'American'
        EGYPTION = 'EG', 'Egyption'

    name = models.CharField(max_length=255)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)])
    opened_at = models.DateField()
    website = models.URLField(default="")
    causine = models.CharField(
        max_length=2, choices=CusineType.choices, default=CusineType.AMERICAN)

    def __str__(self):
        return self.name


class Rating(models.Model):
    # NOTE: This validators are working only on the ModelForm fields .. but not on the database .. so if we write a script that will insert a rating record with minValue = 0 this will work .. so we need to call the full_clean() function before calling the .save() function
    stars = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    comment = models.TextField()
    resturant = models.ForeignKey(
        Resturant, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return f"{self.user.username} - {self.resturant.name} - {self.stars} stars"

    def save(self, *args, **kwargs):
        # this will validate the model fields
        # self.full_clean()
        # This field will be true for the first time we create the object and false if we are updating the object
        print(self._state.adding)
        # this will call the parent class save method
        super().save(*args, **kwargs)


class Sale(models.Model):
    resturant = models.ForeignKey(
        Resturant, on_delete=models.CASCADE, related_name='sales')
    saled_at = models.DateTimeField()
    income = models.DecimalField(max_digits=10, decimal_places=2)


# same staff can work on multiple resturants and same resturant can have multiple staff members
class Staff(models.Model):
    name = models.CharField(max_length=255)
    resturants = models.ManyToManyField(Resturant, related_name='staffs')
