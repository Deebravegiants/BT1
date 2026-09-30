# [H] Potential Limit Order Mis-Triggering From Lagging Cranks

## Summary
Severity: High
Contest weight: 0.3497
Dataset id: 12399
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Levana protocol, cranking works by iterating through all price updates and performing operations for each price update point. One specific operation involves the checking of limit orders with a limit price that is reached by the cranking price. If a limit order is triggered, a new position will be opened at the current price. However, since the position is opened at the current price, there is a possibility of opening a position at an undesirable or worse price than the limit price.
To elaborate, we show below the related code snippet of the limit_order_triggered_order() function. The limit order is triggered if the cranking price is lower than the limit price (line 6). However, the postion is opened with the current price. For example, in the case of a long position, if the limit price is lower than the current price, the trader will get a position at a worse price. This situation may lead to opening a position at an improper price.
```rust
pub(crate) fn limit_order_triggered_order(
    &self,
    storage: &dyn Storage,
    price: Price,
) -> Result<Option<OrderId>> {
    let order = LIMIT_ORDERS_BY_PRICE_LONG
        .prefix_range(
            storage,
            Some(PrefixBound::inclusive(PriceKey::from(price))),
            None,
            Order::Ascending,
        )
        .next();
    let order = match order {
        Some(_) => order,
        None => LIMIT_ORDERS_BY_PRICE_SHORT
            .prefix_range(
                storage,
                None,
                Some(PrefixBound::inclusive(PriceKey::from(price))),
                Order::Descending,
            )
            .next(),
    };
    match order {
        None => Ok(None),
        Some(res) => {
            let ((_, order_id), ()) = res?;
            Ok(Some(order_id))
```

## Recommendation
Revise the above function to make use of the appropriate price to trigger the limit orders.
