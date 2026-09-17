# [M] `Vault` debt interest is never accrued

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1049-L1076
Type: audit-issue

## Details
# `Vault` debt interest is never accrued

## Summary

The `_update_debt` function in the `Vault` contract is responsible for updating internal state to account for any accrued interest since the last update.

However, as the contract is currently implemented, new interest is always `0` because the `last_debt_update` timestamp is updated ahead of the interest calculation.

## Vulnerability Detail

The `_update_debt` function executed the following logic...

```vyper
    self.last_debt_update[_debt_token] = block.timestamp
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )
```

You can see that `self.last_debt_update[_debt_token]` is set to the current block and later `self._debt_interest_since_last_update` is called, passing in the debt token.

The `_debt_interest_since_last_update` function calculates the interest using the following...

```vyper
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE 
        / PRECISION
```

The issue is that `block.timestamp - self.last_debt_update[_debt_token]` will always be `0` as the `last_debt_update` was just updated to the current block.

## Impact

As a result, interest is never accrued for any debt, resulting in a loss of funds for the protocol and LP providers.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1049-L1076

## Tool used

Manual Review

## Recommendation
Calculate the interest before updating the `last_debt_update` timestamp.
