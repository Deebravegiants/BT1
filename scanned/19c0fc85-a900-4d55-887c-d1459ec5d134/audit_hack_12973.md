# [H] Dca orders must have a minimum amount and minimum time in between, otherwise keepers will lose funds

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237
Type: audit-issue

## Details
# Dca orders must have a minimum amount and minimum time in between, otherwise keepers will lose funds

## Summary
Dca orders must have a minimum amount and minimum time in between, otherwise keepers will lose funds

## Vulnerability Detail

There are two issue here and that is why I classified the issue as a high. 

Both issues are all in the `execute_dca_order` function:

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237

The way how the `Dca` orders work is that keepers are monitoring the order and when it is time to execute it, they will call the transaction and execute the order. 

This has 2 main problems with the current implementation:

- A user can specify a `Dca` order to be executed in literally every block
- A user can also specify that order to be of let's say 1 USDC

Problems:

- Keepers will be completely lose a lot of gas in every execution due to having to execute the transaction in every block
- Keepers won't receive a fee because `amount_minus_fee: uint256 = amount_out * (FEE_BASE - self.fee) / FEE_BASE`  it rounds down to 0 if amount is equal to 1.

Therefore keepers will lose funds in every transaction because no fee is reimbursed and they will have to spend a lot of extra gas fees for executing in every block.


## Impact
Keepers will lose funds and not be re-imbursed


## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237

## Tool used

Manual Review

## Recommendation
Add a minimum a amount of time between `Dca` orders and also a minimum amount according to the decimals of every token.
