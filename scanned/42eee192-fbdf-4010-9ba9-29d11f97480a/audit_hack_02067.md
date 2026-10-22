# [M] 7.7 Incorrect Handling of profitFactor

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 2 Code Corrected

The profit factor serves to reduce the profit keepers can make from calling harvest. Thus, following
condition occurs:

```
profitFactor * rewardAmount < want.balanceOf(address(this)) + profit
```
This condition needs to be fulfilled for a reward payment to be made and is hence quite important.

Incorrectly, the condition is unaware of the decimals of the tokens since profitFactor is initialized to
be 100 for any pair. Moreover, it is unaware of the prices of the tokens.

The decimal unawareness may cause the following behaviour:

- Assume the reward token is USDC (6 decimals) and the want token is DAI (18 decimals). The
    condition will almost always pass since profit factor does not account for the base differences
    between the tokens.
- Assume the reward token is DAI (18 decimals) and the want token is USDC (6 decimals). Then, this
    condition will almost never pass to since the reward amount will already be much larger than the
    right-hand-side.

The price unawareness may cause the following behaviour:

- Assume the reward token is AgEUR and one strategy's want token is DAI while for the second one
    the want token is WETH. If now both strategies have similar balances and profits (when converted to
    USD), they will still be treated very differently.

To conclude, inconsistencies in the keeper reward payouts between strategies could occur since the
above condition is unaware of the decimal representation and prices of the tokens.

Code corrected:

profitFactor has been removed. Now, a minimum amount minimumAmountMoved denotes how
much needs to be at least in the contract plus the profits. Also, this amount and the reward amount are
set jointly now to prevent errors.
