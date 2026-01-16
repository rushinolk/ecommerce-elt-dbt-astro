select 
    *,
    ROUND(CAST((price + freight_value) as NUMERIC),2 ) as total_value
from {{source('sources','olist_order_items_dataset')}}