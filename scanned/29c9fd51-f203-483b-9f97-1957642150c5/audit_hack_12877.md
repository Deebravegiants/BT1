# [H] `Vault._update_debt` doesn't accumulate any interest.

## Summary
Severity: High
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058
Type: audit-issue

## Details
# `Vault._update_debt` doesn't accumulate any interest.

## Summary

`Vault._update_debt` is responsible for updating the debt. The interest should be added to the debt. However, `Vault._update_debt` fails to incorporate any interest due to an incorrect  implementation.

## Vulnerability Detail

`Vault._update_debt` first updates `self.last_debt_update[_debt_token]` to `block.timestamp` then calla ` self._debt_interest_since_last_update`
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058
```vyper
def _update_debt(_debt_token: address):
    …

    self.last_debt_update[_debt_token] = block.timestamp
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )
```

Therefore, `_debt_interest_since_last_update` always returns 0 because `block.timestamp - self.last_debt_update[_debt_token]` is always zero.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1071
```vyper
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```


## Impact

No interest is added to the debt. And the interest is lost permanently because `self.last_debt_update[_debt_token]` is updated.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1071


## Tool used

Manual Review

## Recommendation

`Vault._update_debt` should call `self._debt_interest_since_last_update` first then update `self.last_debt_update[_debt_token]`
```diff
def _update_debt(_debt_token: address):
    …

-   self.last_debt_update[_debt_token] = block.timestamp
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )
+   self.last_debt_update[_debt_token] = block.timestamp
```
