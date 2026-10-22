# [M] Missing Slippage Parameter Exposes Users to Unintended Prices, Leading to Potential Fund Loss

## Summary
Severity: Medium
Contest weight: 0.4149
Dataset id: 5755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the trading functions buy and sell, trades are executed based on either the oracle price or a stored constant price, with the higher price being used. While there is a check to ensure price freshness, there is no validation of the price value itself against a reasonable threshold.
In the trading functions buy and sell, trades are executed based on either the oracle price or a stored constant price, with the higher price being used. While there is a check to ensure price freshness, there is no validation of the price value itself against a reasonable threshold. This lack of validation can result in the use of an inflated price from the Pyth oracle due to market volatility, leading to users unknowingly purchasing assets at significantly higher prices. For example, if the stored price and the intended trade price are 100, but the Pyth oracle returns an inflated price of 1000, the system will use 1000, causing a significant loss to the user.

## Recommendation
Introduce a slippage parameter to allow users to specify an acceptable price deviation, ensuring they are protected from extreme price fluctuations. Updated buy Function:
```solidity
impl<'info> Buy<'info> {
pub fn buy(&mut self, amount: u64, max_amount_in: u64) -> Result<()> {
let total_cost = amount * price / 100 * (10000 + self.price.fee)
// Ensure the total cost does not exceed the user's maximum acceptable amount
require!(total_cost <= max_amount_in, CustomError::SlippageExceeded);
Ok(())
}
}
```
