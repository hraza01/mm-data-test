with transformations as (

    select distinct
           mm_user_id
         , type
         , datetime(created_at) as created_at
         , json_extract(location, '$.type') as location_type
         , json_extract(location, '$.coordinates.latitude') as location_latitude
         , json_extract(location, '$.coordinates.longitude') as location_longitude
         , json_extract(trip, '$.metadata.route_session_type') as trip_route_session_type
      from stg_events
     order by type

)

select date(created_at) as status_date
    , mm_user_id, type
    , count(distinct cast(location_latitude as float)) as distinct_lat_coordinates
    , count(distinct cast(location_longitude as float)) as distinct_lon_coordinates
  from transformations
 group by date(created_at)
     , mm_user_id
     , type
