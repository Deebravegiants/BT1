# [M] Loss of yield due to low precision

## Summary
Severity: Medium
Reporter: Bahurum
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419
Type: audit-issue

## Details
# Loss of yield due to low precision

## Summary
In the `Vault` contract function `_mark_as_claimable()` the claimable per share will be lower than expected due to loss of precision. This can also be abused by calling `withdraw_underlying_to_claim()` often.

## Vulnerability Detail
In `Vault` contract at line [419](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419):

```vyper
    self.amount_claimable_per_share += _amount * PRECISION / self.total_shares 
```
`PRECISION = 1e6` and can cause loss of precision of the claimable amount. For example with a yield of 0.1 % a day means 0,000069444 % a minute which corresponds to 6.9444 e-7, which is smaller precision than 1e6. When `withdraw_underlying_to_claim()` is called at intervals of 1 minutes no amount claimable is accounted. If it is called at intervals of 10 minutes then the amount claimed is still underestimated by more than 10%.

## Impact
If `withdraw_underlying_to_claim()` is called often enough the amount claimable will be underestimated and as a result the lenders will have to wait a longer time to get their funds back.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419

## Tool used

Manual Review

## Recommendation
Remove `PRECISION` from the contract and use `DECIMALS` instead, which is 1e18 precision and will avoid precision loss issues.
