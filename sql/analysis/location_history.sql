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
         , datetime(created_at)

)

select distinct
       mm_user_id
     , location_type
     , location_latitude
     , location_longitude
  from transformations
