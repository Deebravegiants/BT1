# [H] Debt doesn't actually acrue

## Summary
Severity: High
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058-L1065
Type: audit-issue

## Details
# Debt doesn't actually acrue

## Summary
Debt does not accrue because of the order of operations in `Vault._update_debt()`. The `last_debt_update` value of the debt token is updated to `block.timestamp` before the calculation used to accrue the `total_debt_amount`. Therefore, positions never accrue any debt.

## Vulnerability Detail
Taking the `_borrow()` function as an example:

```solidity
def _borrow(_debt_token: address, _amount: uint256) -> uint256:
    self._update_debt(_debt_token)

    assert _amount <= self._available_liquidity(_debt_token), "not enough liquidity"

    debt_shares: uint256 = self._amount_to_debt_shares(_debt_token, _amount)

    self.total_debt_amount[_debt_token] += _amount
    self.total_debt_shares[_debt_token] += debt_shares

    return debt_shares
```

The first line that executes is `self._update_debt(_debt_token)` which, in theory, should update the global debt tracker that is used to calculate the `debt_shares_to_amount`.

`self._update_debt()` incorrectly sets the `self.last_debt_update[_debt_token]` to `block.timestamp` before the last line of code which actually accrues the debt by calling `self._debt_interest_since_last_update(_debt_token)`:

```solidity
@internal
def _update_debt(_debt_token: address):

    if block.timestamp == self.last_debt_update[_debt_token]:
        return  # already up to date, nothing to do

    self.last_debt_update[_debt_token] = block.timestamp
    
    self.total_debt_amount[_debt_token] += self._debt_interest_since_last_update(
        _debt_token
    )
```

**self._debt_interest_since_last_update(_debt_token):**
```solidity
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```

Since `block.timestamp` will always equal `block.timestamp`, the accrued debt will always be **0**.

## Impact
- Debt never accrues
- Positions borrow for free
- LPs don't earn yield for their risk

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1058-L1065

## Tool used
Manual Review

## Recommendation
Move the `self.last_debt_update[_debt_token] = block.timestamp` to the end of the `_update_debt()` function.
