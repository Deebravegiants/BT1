# [H] Vault.vy: Faulty Interest Calculation in Vault.vy due to Improper Update Sequence

## Summary
Severity: High
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1049-L1076
Type: audit-issue

## Details
# Vault.vy: Faulty Interest Calculation in Vault.vy due to Improper Update Sequence

## Summary
An error in the sequence of operations in `Vault.vy.update_debt` function results in no increase in debt, thereby affecting the accurate calculation of interest.

## Vulnerability Detail
The function `_debt_interest_since_last_update` in `Vault.vy` calculates the interest on debt by comparing the current time and `last_debt_update` to add the corresponding interest.

```vyper
@internal
@view
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```

However, in the `_update_debt` function, where this is implemented, `last_debt_update` is updated to `block.timestamp` before the call to `_debt_interest_since_last_update`.

```vyper
@internal
def _update_debt(_debt_token: address):
    """
    @notice
        Accounts for any accrued interest since the last update.
    """
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do

    self.last_debt_update[_debt_token] = block.timestamp # <<- UPDATE HERE
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update( #@audit always adds 0
        _debt_token
    )
```
This update sequence results in `_debt_interest_since_last_update` always returning 0, hence no increase in debt is observed.

## Impact
The faulty interest calculation impacts the accurate management of debt, causing a discrepancy between the expected and actual debt increase. This may affect the protocol's financial integrity and disrupt users' trade strategies.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1049-L1076

## Tool used

Manual Review

## Recommendation
Reorder the sequence of operations in the `_update_debt` function to ensure that `_debt_interest_since_last_update` is called before `last_debt_update` is updated to `block.timestamp`. This will ensure that the correct amount of interest is added to the total debt amount.
