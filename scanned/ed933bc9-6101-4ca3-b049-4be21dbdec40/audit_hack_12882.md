# [H] The debt interest always evaluating to zero

## Summary
Severity: High
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050-L1076
Type: audit-issue

## Details
# The debt interest always evaluating to zero

## Summary
The debt interest always evaluating to zero
## Vulnerability Detail
 The `_update_debt()` function first updates self.last_debt_update[_debt_token] with the current block timestamp and then calls _debt_interest_since_last_update, which subtracts self.last_debt_update[_debt_token] from the current block timestamp. This results in the calculation (block.timestamp - self.last_debt_update[_debt_token]) always evaluating to zero.
```solidity
def _update_debt(_debt_token: address):
    """
    @notice
        Accounts for any accrued interest since the last update.
    """
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do

    self.last_debt_update[_debt_token] = block.timestamp
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )

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

## Impact
The debt interest always evaluating to zero.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050-L1076
## Tool used

Manual Review

## Recommendation
To resolve this issue and accurately calculate the debt interest, the sequence of operations should be reversed. The _debt_interest_since_last_update function should be called first to calculate the interest based on the existing self.last_debt_update[_debt_token]. Then, self.last_debt_update[_debt_token] should be updated with the current block timestamp.
