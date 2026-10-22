# [M] Missing Confidence Validation in Pyth Oracle Price

## Summary
Severity: Medium
Contest weight: 0.4077
Dataset id: 5756
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The trading functions that use the Pyth oracle price do not validate confidence values (conf and ema_conf). They only use get_price_no_older_than to check staleness but do not ensure that the confidence percentage remains within an acceptable threshold. This omission can lead to:
• Using prices during high uncertainty periods, which may not reflect accurate market conditions.
• Missing market anomaly signals, potentially overlooking extreme price deviations.
• Potential incorrect liquidations during low market confidence, leading to unfair liquidations or improper risk calculations.
As per Pyth's best practices, confidence intervals should be considered when evaluating price validity.

## Recommendation
Introduce a configurable max_confidence_pct parameter in the price account and validate the confidence percentage before using the price.
• Updated buy Function with Confidence Validation:
```solidity
impl<'info> Buy<'info> {
pub fn buy(&mut self, amount: u64, max_amount_in: u64, max_confidence_pct: u64) -> Result<()> {
// Fetch price and confidence from Pyth oracle
let pyth_price_result =
price_update.get_price_no_older_than(&Clock::get()?, maximum_age, &feed_id);
let (pyth_price, conf) = match pyth_price_result {
Ok(price) => (price.price, price.conf),
Err(e) => Err(e)?,
};
// Validate confidence percentage.
let confidence_pct = (conf as u128)
.checked_mul(100)?
.checked_div(pyth_price.abs() as u128)?;
require!(
confidence_pct <= max_confidence_pct as u128,
CustomError::PriceConfidenceTooHigh
);
Ok(())
}
}
```
