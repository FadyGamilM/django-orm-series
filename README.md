# django-orm-series
learning django orm from this course : `https://www.youtube.com/playlist?list=PL-2EBeDYMIbQXKsyNweppuFptuogJe2L-`

# Modeling Data From Django To Actual DB:
1. Naming the FK fields as `[resource]` will reflect on the database as `[resource]_id`.
2. Not Specifying the `id` field and let django define it will mark it as `serialize=False` and won't be serialzied to json.