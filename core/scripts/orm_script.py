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

    # print(is_validtion_working_on_db_level_by_default())
    # print(is_validtion_working_on_db_level_by_default_with_right_vaidation())

    # update_resturant_name()

    # get_all_ratings_and_their_related_resturants_optimized_starting_from_many_part()

    # get_all_5_stars_ratings_resturants_and_fetch_their_sales_starting_with_ratings()

    get_all_5_stars_ratings_resturants_and_fetch_their_sales_starting_with_resturants()

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


def update_resturant_name():
    resturant = Resturant.objects.first()
    resturant.name = 'indian spices - newyork branch'
    # resturant.save() > This will update the entire fields alongside the field/s we need to update and this is costly for large db tables .. so to optimize this we add this argument `updated_fields=['field1_name', 'field2_name', ....]`
    resturant.save(update_fields=['name'])


def update_resturant_name_with_filter():
    no_of_updated_resturant = Resturant.objects.filter(name__icontains='Spice').update(
        opened_at=timezone.now() - timezone.timedelta(days=365))
    print(no_of_updated_resturant)
    return


def get_all_resturants_with_ratings_optimized_starting_from_one_part():
    '''
    In this function i am demonstrating the fix of the N+1 problem when we start/have the one-side of the one-to-many relation and we want to avoid N+1 queries for the many-side of the one-to-many --> so here we have the resturant and we want to prefetch all ratings 
    '''
    # prefetch the related ratings and sales
    # and for sales also prefetch the related user at once
    resturants = Resturant.objects.prefetch_related('ratings__user', 'sales')
    for resturant in resturants:
        print(f"{resturant.name}: {[str(r) for r in resturant.ratings.all()]}")


def get_all_ratings_and_their_related_resturants_optimized_starting_from_many_part():
    '''
    In this function i am demonstrating the fix of the N+1 problem when we start/have the many-side of the one-to-many relation and we want to avoid N+1 queries for the one-side of the one-to-many --> so here we have the rating and we want to prefetch all resturants 
    ==> This will make a single Join query and this is better than the above but each one has it's own usecase
    '''
    ratings = Rating.objects.filter(
        stars__gt=2).select_related('resturant', 'user')
    for rating in ratings:
        print(f"{rating.resturant.name}: {rating.stars}, {rating.comment}")


def get_all_5_stars_ratings_resturants_and_fetch_their_sales_starting_with_ratings():
    """
    This is the way i think about this query : 
    SELECT ru.id, ru.name, s.income, r.stars
    FROM Rating as r JOIN Resturant as ru ON ru.id = r.resturant_id
    WHERE r.stars = 5 
    JOIN Sales as s ON s.resturant_id = r.id;
    """
    ratings_with_5stars = Rating.objects.filter(
        stars=5).select_related('resturant').prefetch_related('resturant__sales')
    for rating in ratings_with_5stars:
        print(f"{rating.resturant.name}: {rating.stars}, {rating.comment}")
        for sale in rating.resturant.sales.all():
            print(f"Sale: {sale.income} at {sale.saled_at}")


def get_all_5_stars_ratings_resturants_and_fetch_their_sales_starting_with_resturants():
    """
    This is the way i think about this query : 
    SELECT ru.id, ru.name, s.income, r.stars
    FROM Rating as r JOIN Resturant as ru ON ru.id = r.resturant_id
    WHERE r.stars = 5 
    JOIN Sales as s ON s.resturant_id = r.id;
    """
    resturants_with_5stars_ratings = Resturant.objects.prefetch_related(
        'ratings', 'sales').filter(ratings__stars=5)
    print(resturants_with_5stars_ratings)
    # Executed Queries via ORM:
    # 1. Resturant Join Ratings to get resturants data with ratings = 5
    # -------> (issue) after it joins the two tables, it fetches the Resturant fields only due to orm behavior
    # 2. Select From Ratings again where resturant_id IN the selected Resturants from query.1
    # -------> (why) this query due to the prefetch_related('ratings')
    # 3. select From Sales where resturant_id IN the selected Resturants from query.1
