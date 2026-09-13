# [H] Rounding errors in `_calc_min_amount_out()` function

## Summary
Severity: High
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L270-L274
Type: audit-issue

## Details
# Rounding errors in `_calc_min_amount_out()` function

## Summary
Rounding errors in `_calc_min_amount_out()` function
## Vulnerability Detail
The function `_calc_min_amount_out()` is used to calculate the minimum amount of tokens that should be received as output given an input amount, a token path, fees, TWAP (Time-Weighted Average Price) parameters, and maximum slippage.
When performing consecutive divisions in calculations, there can be a loss of precision due to the limited number of decimal places that can be represented in fixed-point arithmetic. This loss of precision can result in rounding errors and deviations from the exact mathematical result.

Each division operation introduces a potential for rounding errors. The result of one division becomes the input for the next division, and this process continues for each subsequent division. With each division, the number of significant digits or decimal places in the result may decrease.
```solidity
    min_amount_out: uint256 = _amount_in * PRECISISON 
    min_amount_out = min_amount_out * twap_value
    min_amount_out = (min_amount_out * (FEE_BASE - uni_fees_total - _max_slippage)) / FEE_BASE
    min_amount_out = min_amount_out / 10**token_in_decimals
    min_amount_out = min_amount_out / PRECISISON
```

## Impact
This loss of precision can accumulate throughout the consecutive division operations, potentially affecting the final result. The more divisions performed, the greater the cumulative impact of the rounding errors.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L270-L274
## Tool used

Manual Review

## Recommendation
To mitigate this issue, it is important to consider the order of operations and carefully handle the precision and rounding requirements in the calculations. Using appropriate rounding methods or scaling techniques, such as using higher precision arithmetic or intermediate rounding steps, can help minimize the impact of precision loss in consecutive divisions.
