# [M] Incorrect rounding direction when calculating the seized collateral from the borrower

## Summary
Severity: Medium
Contest weight: 0.2083
Dataset id: 9798
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidatePosition() function in liquidate.lua transfers out the underlying token of a given quantity. It calculates how many oTokens the transferred underlying tokens are worth and subtract that value from the borrower's position. The value, qtyValueInoToken, is calculated as: -- get supplied quantity value -- (total supply / total pooled) * incoming local qtyValueInoToken = bint.udiv( totalSupply * quantity, totalPooled ) where totalSupply is the oToken's total supply, and totalPooled is the sum of total borrows and cash in the market. The bint.udiv() performs an integer division with the result rounded down, which benefits the borrower as their oToken balance is subtracted with a smaller value. The rounding error may be insignificant if totalSupply and totalPooled are large enough. However, in an empty-market attack scenario, where the attacker artificially inflates the market's exchange rate, the rounding error could become large enough to cause issues with the protocol. For example, assuming an attacker can inflate the exchange rate such that 1 oToken is worth 100,000 underlying tokens. If the repay value is less than 100,000 underlying tokens, qtyValueInoToken will be 0. As a result, the borrower will not incur a loss while being liquidated. However, the oToken still transfers the quantity amount of underlying tokens to the liquidator. Regarding how an attacker can inflate the exchange rate on an empty market, see the finding Security considerations of exchange-rate inflation in empty markets.

## Recommendation
Consider implementing a helper function that rounds up the division result to calculate the qtyValueInoToken value. Also, consider implementing security measures and checks to mitigate potential exchange-rate inflation attacks on empty markets.
