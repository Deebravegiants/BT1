# [H] The vault interest was miscalculated

## Summary
Severity: High
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050-L1076
Type: audit-issue

## Details
# The vault interest was miscalculated

## Summary

`_update_debt` implementation error, can not realize the interest calculation, interest is always zero.

## Vulnerability Detail

```vyper
@internal
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

`_update_debt` will set `self.last_debt_update[_debt_token] = block.timestamp`, so `_debt_interest_since_last_update` always return `0`

## Impact

Unable to achieve interest calculation, users can borrow interest-free, affecting the protocol and staking users income.
This will also affect the internal accounting system, because `amount_per_debt_share` / `debt_shares_to_amount` all contain correctly calculated interest, which will lead to bookkeeping confusion. 

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050-L1076

## Tool used

Manual Review

## Recommendation

Calculate the interest first, and then update 'self.last_debt_update[_debt_token] = block.timestamp'
