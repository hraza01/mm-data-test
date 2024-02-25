with transformations as (

    select distinct
           mm_user_id, type
         , datetime(created_at) as created_at
         , json_extract(location, '$.type') as location_type
         , json_extract(location, '$.geohash') as location_geohash
      from stg_events
     order by datetime(created_at)

)

select date(created_at) as status_date
     , mm_user_id, type
     , leftstr(location_geohash, 8) as geohash_prefix
     , count(distinct location_geohash) as distinct_geohashes

  from transformations
 group by date(created_at)
     , mm_user_id
     , type
     , leftstr(location_geohash, 8)
