# [H] Vault.vy#L1050C5-L1050C17 : function `_update_debt` will not update the debt since it reset the time before calculating the interest accrued.

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050C5-L1050C17
Type: audit-issue

## Details
# Vault.vy#L1050C5-L1050C17 : function `_update_debt` will not update the debt since it reset the time before calculating the interest accrued.

## Summary

Function [_update_debt](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1050C5-L1050C17) resets the [last_debt_update](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058C10-L1058C26) as current time, before calculating the interest accrued. This will lead to no interest calculation.

## Vulnerability Detail

contract has the `_update_debt` function to update the interest accrued over a period of time.  to store the last updated time , there is variable `last_debt_update` which is used to track last updated time.

`_update_debt` is called to update the interset value prior to performing any accounting related functions such as borrow , repay , liquidate and so.

as shown below, the `last_debt_update` is set as block.timestamp, and then the interest value is calculated by using `_debt_interest_since_last_update`

```vyper
 @internal
def _update_debt(_debt_token: address):
    """
    @notice
        Accounts for any accrued interest since the last update.
    """
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do


    self.last_debt_update[_debt_token] = block.timestamp ---------------->>> time is updated.
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest


    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update( ---------------->>> interest is calculated.
        _debt_token
    )
```
```vyper
@internal
@view
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token]) ---------->>> here the subtracted would be zero, since last_debt_update already set as block.timestamp.
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```
 
## Impact

No interest would be accrued. It would be loss either to the protocol or user.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1049-L1076

## Tool used

Manual Review

## Recommendation

Update the changes as shown below inside the function `_update_debt`

```vyper
@internal
def _update_debt(_debt_token: address):
    """
    @notice
        Accounts for any accrued interest since the last update.
    """
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do


    self.last_debt_update[_debt_token] = block.timestamp ---------------->>>> remove this line
    
    if self.total_debt_amount[_debt_token] == 0:
        return # no debt, no interest


    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token

    self.last_debt_update[_debt_token] = block.timestamp ---------------->>>> add this line
    )
```
