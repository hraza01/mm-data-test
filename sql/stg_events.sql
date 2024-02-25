drop table stg_events;
create table stg_events as

with raw as (

    select id
         , json(payload) as payload
      from webhook_data

)

, base as (

    select id
         , json_extract(payload, '$.id') as pid
         , json_extract(payload, '$.live') as live
         , json_extract(payload, '$.type') as type
         , json_extract(payload, '$._id') as payload_id
         , json_extract(payload, '$.MMUserId') as mm_user_id
         , json_extract(payload, '$.created_at') as created_at
         , json_extract(payload, '$.location') as location
         , json_extract(payload, '$.trip') as trip
    from raw
)

select *
  from base;
