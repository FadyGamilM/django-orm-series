from core.models import Resturant, Rating, Sale
from django.utils import timezone
from django.db import connection
from django.contrib.auth.models import User
from django.db import transaction
from pprint import pprint


def run():
    print('------------------ orm_script started execution ------------------')
    # create_resturant_record_1()

    # resurant = select_first_resurant()
    # print(f'first resurant is {resurant} ')

    # rate_resturant_1()

    # rate_resturant_1_optimized()

    # filter_rates_by_stars(4)

    # get_resturant_name_by_rating_id(1)

    # get_ratings_given_resturant()

    # get_user_rating_on_specific_resturant_or_create_new_one(1, 2)

    print(is_validtion_working_on_db_level_by_default())

    print(is_validtion_working_on_db_level_by_default_with_right_vaidation())

    for query in connection.queries:
        print()
        print(query)
        print()
    print('------------------ orm_script finished execution ------------------')


def create_resturant_record_1():
    resurant = Resturant()
    resurant.name = 'Italizano'
    resurant.latitude = 50.3
    resurant.longitude = 50.301
    resurant.causine = resurant.CusineType.ITALIAN
    resurant.opened_at = timezone.now()

    resurant.save()


def select_first_resurant() -> Resturant:
    # so far the SELECT statment query is not executed yet
    first_resurant = Resturant.objects.first()
    return first_resurant  # once we use the fetched data .. the query will be executed


def rate_resturant_1():
    with transaction.atomic():
        resturant = Resturant.objects.first()
        user = User.objects.first()
        rating = Rating()
        rating.stars = 4
        rating.comment = 'Great food'
        rating.resturant = resturant
        rating.user = user

        rating.save()


def rate_resturant_1_optimized():
    with transaction.atomic():
        resturant_id = Resturant.objects.only('id').all()[1]
        user_id = User.objects.only('id').first()
        rating = Rating()
        rating.stars = 4
        rating.comment = 'Great food'
        rating.resturant = resturant_id
        rating.user = user_id

        rating.save()


def filter_rates_by_stars(stars):
    with transaction.atomic():
        ratings = Rating.objects.filter(stars__gt=stars)
        print(f'found {len(ratings)} ratings with stars {stars}')


def get_resturant_name_by_rating_id(rating_id):
    rating = Rating.objects.get(id=rating_id)
    resturant = rating.resturant  # NOT VALID and NOT COMPILED
    print(f'resturant name is {resturant.name} ')


def get_ratings_given_resturant():
    resturant = Resturant.objects.first()
    ratings = resturant.ratings.all()
    print(ratings)


def get_user_rating_on_specific_resturant_or_create_new_one(user_id, resturant_id):
    with transaction.atomic():
        resturant = Resturant.objects.get(id=resturant_id)
        user = User.objects.get(id=user_id)
        rating, is_created = Rating.objects.get_or_create(
            resturant=resturant,
            user=user,
            stars=3
        )
        if is_created:
            print('rating created')
        else:
            print('rating already exists')
    print(rating)


def is_validtion_working_on_db_level_by_default() -> Rating:
    resturant = Resturant.objects.all()[1]
    user = User.objects.first()
    rating = Rating(resturant=resturant, user=user, stars=9)
    rating.save()
    return rating


def is_validtion_working_on_db_level_by_default_with_right_vaidation() -> Rating:
    resturant = Resturant.objects.all()[1]
    user = User.objects.first()
    rating = Rating(resturant=resturant, user=user, stars=9)
    rating.full_clean()
    rating.save()
    return rating
