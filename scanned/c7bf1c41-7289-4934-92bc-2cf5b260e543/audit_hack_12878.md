# [H] Debts do not accrue interest due to logic error

## Summary
Severity: High
Reporter: 0x00ffDa
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L1050
Type: audit-issue

## Details
# Debts do not accrue interest due to logic error

## Summary
When attempting to update the cumulative interest on a debt, the calculation of new interest always results in 0.

## Vulnerability Detail
Vault [` _update_debt()`](https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L1050) attempts to accrue debt interest if time has passed since the last call. This is used prior to letting a user borrow, repay, or adjust liquidity. After verifying that time has passed since the prior update, this function updates the timestamp for this update **before** that timestamp value gets used in the interest calculation by the Vault `_debt_interest_since_last_update()` function.

This results in the following calculation
```javascript
block.timestamp - self.last_debt_update[_debt_token]
```
... to be equivalent to
```javascript
block.timestamp - block.timestamp
```
... and yield a time delta of `0`. With no time passage detected, the accrued interest calculation also yields 0 and the debt remains unchanged.

## Impact
Debts never accrue interest, causing lost revenue for the protocol.

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L1050
```javascript
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
```

```javascript
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```

## Tool used

Manual Review

## Recommendation
Modify the logic of `_update_debt()` to update the timestamp after accrual:
```javascript
    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do
    
    if self.total_debt_amount[_debt_token] > 0:    
        self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
            _debt_token 
        )

    self.last_debt_update[_debt_token] = block.timestamp
```
Add tests that verify debt interest accrual over time.
