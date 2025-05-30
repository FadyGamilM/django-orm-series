from functools import partial
from core.models import Resturant, Rating, Sale, Staff
from django.utils import timezone
from django.db import connection
from django.contrib.auth.models import User
from django.db import transaction
from pprint import pprint
from django.db.models import Sum, Prefetch
from django.db.models import *
from django.db.models.functions import Length, Coalesce


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

    # get_all_5_stars_ratings_resturants_and_fetch_their_sales_starting_with_resturants()

    # insert_sale_record()

    # get_5_stars_resturants_total_sales()

    # get_5_stars_resturants_total_sales_for_x_months_ago_v1(1)

    # create_staff_memeber_record()

    # remove_resturant_from_staff_resturants()

    # update_existing_association_relation()

    # filter_associations_for_staff()

    # filter_associations_for_resturant()

    # select_with_specific_values_only()

    # select_resturant_names_with_italian_cusine_having_ratings_less_than3()

    # select_avg_sales_amount()

    # get_resturant_name_and_total_sales_per_resturant()

    # get_resturant_rating_per_resturant_causine()

    # update_rating_not_optimized()

    # update_rating_oprimized()

    # update_rating_optimized_v2()

    protect_your_app_from_null_values_using_coalesce()

    for query in connection.queries:
        print()
        print(query)
        print()
    print('------------------ orm_script finished execution ------------------')


def create_resturant_record_1():
    resurant = Resturant()
    resurant.name = 'mo bistro'
    resurant.latitude = 55.0
    resurant.longitude = 55.1
    resurant.causine = resurant.CusineType.EGYPTION
    resurant.opened_at = timezone.now() - timezone.timedelta(days=365*3)

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
    try:
        with transaction.atomic():
            resturant = Resturant.objects.last()
            if resturant is None:
                print('resturant not found')
                return
            user = User.objects.only('id').first()
            if user is None:
                print('user not found')
                return
            rating = Rating()
            rating.stars = 4
            rating.comment = 'Great food'
            rating.resturant = resturant
            rating.user = user

            rating.save()
    except Exception as ex:
        print(f'failed to rate a resturant with error = {ex}')


def filter_rates_by_stars(stars):
    with transaction.atomic():
        ratings = Rating.objects.filter(stars__gt=stars)
        print(f'found {len(ratings)} ratings with stars {stars}')


def get_resturant_name_by_rating_id(rating_id):
    rating = Rating.objects.get(id=rating_id)
    resturant = rating.resturant
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


def insert_sale_record():
    resturant = Resturant.objects.all()[1]
    sale = Sale()
    sale.resturant = resturant
    sale.income = 5060
    sale.saled_at = timezone.now() - timezone.timedelta(days=1)
    sale.save()

# Grouping by a field in a many-side relation table


def get_5_stars_resturants_total_sales():
    result = Resturant.objects.prefetch_related('ratings', 'sales').filter(
        ratings__stars=5).annotate(total_sales_sum=Sum('sales__income'))
    print(result)


def get_5_stars_resturants_total_sales_for_x_months_ago_v1(num_of_months_ago):
    months_ago_duration = timezone.now() - timezone.timedelta(days=30*num_of_months_ago)
    result = Resturant.objects.prefetch_related('ratings', 'sales').filter(
        ratings__stars=5, sales__saled_at__gte=months_ago_duration).annotate(total_sales_sum=Sum('sales__income'))
    print(result)


def get_5_stars_resturants_total_sales_for_x_months_ago_v2(num_of_months_ago):
    months_ago_duration = timezone.now() - timezone.timedelta(days=30*num_of_months_ago)
    prefetch_sales = Prefetch('sales', queryset=Sale.objects.filter(
        saled_at__gte=months_ago_duration))
    result = Resturant.objects.prefetch_related('ratings', prefetch_sales).filter(
        ratings__stars=5).annotate(total_sales_sum=Sum('sales__income'))
    print(result)


def create_staff_memeber_record():
    '''
    {'sql': 'INSERT INTO "core_staff" ("name") VALUES (\'ahmed mostafa\') RETURNING "core_staff"."id"', 'time': '0.000'}


    {'sql': 'SELECT "core_resturant"."id", "core_resturant"."name", "core_resturant"."latitude", "core_resturant"."longitude", "core_resturant"."opened_at", "core_resturant"."website", "core_resturant"."causine" FROM "core_resturant" ORDER BY "core_resturant"."id" ASC LIMIT 1', 'time': '0.000'}


    {'sql': 'BEGIN', 'time': '0.000'}


    {'sql': 'INSERT OR IGNORE INTO "core_staff_resturants" ("staff_id", "resturant_id") VALUES (1, 1)', 'time': '0.000'}


    {'sql': 'COMMIT', 'time': '0.000'}
    '''
    staff = Staff()
    staff.name = 'ahmed mostafa'
    staff.save()
    staff.resturants.add(Resturant.objects.first())


def remove_resturant_from_staff_resturants():
    '''
    {'sql': 'SELECT "core_staff"."id", "core_staff"."name" FROM "core_staff" ORDER BY "core_staff"."id" ASC LIMIT 1', 'time': '0.000'}


    {'sql': 'SELECT "core_resturant"."id", "core_resturant"."name", "core_resturant"."latitude", "core_resturant"."longitude", "core_resturant"."opened_at", "core_resturant"."website", "core_resturant"."causine" FROM "core_resturant" ORDER BY "core_resturant"."id" ASC LIMIT 1', 'time': '0.000'}


    {'sql': 'BEGIN', 'time': '0.000'}


    {'sql': 'DELETE FROM "core_staff_resturants" WHERE ("core_staff_resturants"."staff_id" = 1 AND "core_staff_resturants"."resturant_id" IN (1))', 'time': '0.000'}


    {'sql': 'COMMIT', 'time': '0.000'}
    '''
    staff = Staff.objects.first()
    print(staff.resturants)
    staff.resturants.remove(Resturant.objects.first())
    print(staff.resturants)


def update_existing_association_relation():
    '''
    query if you are calling this function for the first time:
    > 
        3
        {'sql': 'SELECT "core_staff"."id", "core_staff"."name" FROM "core_staff" WHERE "core_staff"."name" = \'ahmed mostafa\' LIMIT 21', 'time': '0.000'}


        {'sql': 'SELECT "core_resturant"."id", "core_resturant"."name", "core_resturant"."latitude", "core_resturant"."longitude", "core_resturant"."opened_at", "core_resturant"."website", "core_resturant"."causine" FROM "core_resturant" LIMIT 3', 'time': '0.000'}


        {'sql': 'BEGIN', 'time': '0.000'}


        {'sql': 'SELECT "core_resturant"."id" AS "id" FROM "core_resturant" INNER JOIN "core_staff_resturants" ON ("core_resturant"."id" = "core_staff_resturants"."resturant_id") WHERE "core_staff_resturants"."staff_id" = 1', 'time': '0.000'}


        {'sql': 'INSERT OR IGNORE INTO "core_staff_resturants" ("staff_id", "resturant_id") VALUES (1, 1), (1, 2), (1, 3)', 'time': '0.000'}


        {'sql': 'COMMIT', 'time': '0.000'}


        {'sql': 'SELECT COUNT(*) AS "__count" FROM "core_staff_resturants" WHERE "core_staff_resturants"."staff_id" = 1', 'time': '0.000'}

    query if you are calling this function for the second time:
    >
        3
        {'sql': 'SELECT "core_staff"."id", "core_staff"."name" FROM "core_staff" WHERE "core_staff". "name" = \'ahmed mostafa\' LIMIT 21', 'time': '0.000'}


        {'sql': 'SELECT "core_resturant"."id", "core_resturant"."name", "core_resturant"."latitude", "core_resturant"."longitude", "core_resturant"."opened_at", "core_resturant"."website", "core_resturant"."causine" FROM "core_resturant" LIMIT 3', 'time': '0.000'}


        {'sql': 'BEGIN', 'time': '0.000'}


        {'sql': 'SELECT "core_resturant"."id" AS "id" FROM "core_resturant" INNER JOIN "core_staff_resturants" ON ("core_resturant"."id" = "core_staff_resturants"."resturant_id") WHERE "core_staff_resturants"."staff_id" = 1', 'time': '0.000'}


        {'sql': 'COMMIT', 'time': '0.000'}


        {'sql': 'SELECT COUNT(*) AS "__count" FROM "core_staff_resturants" WHERE "core_staff_resturants"."staff_id" = 1', 'time': '0.000'}

    django orm is smart enough to know that the relation is already exists and it will not create a new one, if you run this query again 
    '''
    staff_ahmed_mostafa = Staff.objects.get(name='ahmed mostafa')
    staff_ahmed_mostafa.resturants.set(Resturant.objects.all()[:3])
    print(staff_ahmed_mostafa.resturants.count())


def clear_all_associations_for_staff():
    staff = Staff.objects.get(name='ahmed mostafa')
    staff.resturants.clear()
    print(staff.resturants.count())


def filter_associations_for_staff():
    staff = Staff.objects.get(name='ahmed mostafa')
    staff_resturants = staff.resturants.filter(name__icontains='marino')
    print(staff_resturants)


def filter_associations_for_resturant():
    resturant = Resturant.objects.get(pk=1)
    resturant_staff = resturant.staffs.filter(name__icontains='ahmed')
    print(resturant_staff)


# selecting one object will return a dict
# selecting multiple objects will return a queryset
def select_with_specific_values_only():
    resturant = Resturant.objects.values(
        'name', 'opened_at', 'causine').first()
    print(resturant)


def select_resturant_names_with_italian_cusine_having_ratings_less_than3():
    result = Rating.objects.filter(
        stars__lt=3).values('resturant__name', 'stars')
    print(result)


def select_avg_sales_amount():
    res = Sale.objects.aggregate(Avg('income'), Sum('income'))
    print(res)


def get_resturant_name_and_total_sales_per_resturant():
    res = Resturant.objects.annotate(total_sale=Sum(
        'sales__income')).values('name', 'total_sale')
    print(res)


def get_resturant_rating_per_resturant_causine():
    res = Resturant.objects.values('causine').annotate(Count('ratings'))
    print(res)


def update_rating_not_optimized():
    '''usually, when we need to update a record, we pull it in your app memory .. update the value and send it back, and this is what django will do if we did the following : '''
    rating = Rating.objects.first()
    rating.stars += 1
    rating.save()
    # this is the query : {'sql': 'UPDATE "core_rating" SET "stars" = 5, "comment" = \'Great food\', "resturant_id" = 1, "user_id" = 1 WHERE "core_rating"."id" = 1', 'time': '0.001'}
    # so we say set stars = 5 which is taken from the updated value from python app memory


def update_rating_oprimized():
    def send_email(email):
        print(f'sending email to {email}')
    with transaction.atomic():
        rating = Rating.objects.first()
        rating.stars = F('stars') + 1
        rating.save()
        # Todo : to access the stars value after this combinedExpression update, we should call a refresh_from_db() method on the model object
        rating.refresh_from_db()
        print(rating.stars)
        # this is the query : {'sql': 'UPDATE "core_rating" SET "stars" = ("core_rating"."stars" + 1), "comment" = \'Great food\', "resturant_id" = 1, "user_id" = 1 WHERE "core_rating"."id" = 1', 'time': '0.001'}
        # now we are using the value from the database directly
    # this is how you can call a function with param using partial and how to trigger a functions defined for being executed after the transaction is committed
    transaction.on_commit(partial(send_email, 'gamilfady605@gmail.com')) 

#! so basiaclly F() expressions are used to avoid pulling the columns that will be updated in the memory and do the update on the db level


def update_rating_optimized_v2():
    '''and this is the most optimized version of the update with f expression'''
    rating = Rating.objects.filter(pk=1).update(
        stars=F('stars') - 1
    )
    # this is the query : {{'sql': 'UPDATE "core_rating" SET "stars" = ("core_rating"."stars" - 1) WHERE "core_rating"."id" = 1', 'time': '0.001'}}


def get_itialian_or_egyption_resturants():
    resturants = Resturant.objects.filter(
        Q(causine=Resturant.CusineType.ITALIAN) | Q(
            causine=Resturant.CusineType.EGYPTION)
    )
    print(resturants)


def protect_your_app_from_null_values_using_coalesce():
    res = Rating.objects.filter(stars__lt=0).aggregate(
        sum_of_rating=Coalesce(Sum('stars'), 0))
    print(res)
