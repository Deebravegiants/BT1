# [H] Interest Calculation is bricked and interest is never accured in `_update_debt` function

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058
Type: audit-issue

## Details
# Interest Calculation is bricked and interest is never accured in `_update_debt` function

## Summary
While calculating the interest and adding it to the total debt the calculation is bricked as the the timestamp is updated to block.timestamp before doing the necessary calculation in the `_debt_interest_since_last_update` function.
## Vulnerability Detail
While borrinwg, repaying, providing and removing liquidity, function `update_debt` is called which updates the debt amount by adding interest to it which is accumulated over a time intereval.

But the problem in the following code snippet is:

```solidity
def _update_debt(_debt_token: address):
    """
    @notice
        Accounts for any accrued interest since the last update.
    """
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do
    # @audit updated before calculating the result
    self.last_debt_update[_debt_token] = block.timestamp
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest

    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )

@internal
@view
# @note - who is paying this interest and how is this interest being paid
def _debt_interest_since_last_update(_debt_token: address) -> uint256:

    return (

        (block.timestamp - self.last_debt_update[_debt_token])* self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE 
        / PRECISION
    )
```

In the following line:

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058

the time stamp is updated to the latest timestamp, and than we call `_debt_interest_since_last_update` which calculates based upon the difference between the block.timestamp and value stored in `last_debt_update` which is now also block.timestamp, so it becomes zero and interest accured is alway zero.
```solidity
     # @audit-issue (0) *  self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE 
        / PRECISION ==== 0
     (block.timestamp - self.last_debt_update[_debt_token])* self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE 
        / PRECISION
```
## Impact
Interest is never accured on the debt, so no one will ever pay the interest.
## Code Snippet

## Tool used

Manual Review

## Recommendation
Update the latest  timestamp in the function _debt_interest_since_last_update or after calling it
