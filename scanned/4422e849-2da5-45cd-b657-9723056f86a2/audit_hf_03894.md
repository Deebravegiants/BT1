# [H] reduce_position doesn’t update margin map-

## Summary
Severity: High
Contest weight: 0.7679
Dataset id: 20183
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
debt_amount: uint256 = self._debt(_position_uid)
margin_debt_ratio: uint256 = position.margin_amount * PRECISION / debt_amount
amount_out_received: uint256 = self._swap(
    position.position_token, position.debt_token, _reduce_by_amount,
    min_amount_out
)
# reduce margin and debt, keep leverage as before
reduce_margin_by_amount: uint256 = (
    amount_out_received * margin_debt_ratio / PRECISION
)
reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount
position.margin_amount -= reduce_margin_by_amount
burnt_debt_shares: uint256 = self._repay(position.debt_token, reduce_debt_by_amount)
position.debt_shares -= burnt_debt_shares
position.position_amount -= _reduce_by_amount
```
reduce_position function decrease the margin amount of the position but doesn't add it back to the user's margin mapping, making it impossible to withdraw the margin. After selling some position tokens back against debt tokens using reduce_position function, debt_shares and margin_amount are reduced proportionally to keep leverage the same as before: Vault.vy#L313-L330. However, even though some of the margin have been paid back (position.margin_amount has been reduced), self.margin[position.account][position.debt_token] mapping hasn't been updated by adding reduce_margin_by_amount which would allow the user to withdraw his margin. Users will lose their margin tokens.

## Recommendation
```solidity
reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount
position.margin_amount -= reduce_margin_by_amount
self.margin[position.account][position.debt_token] += reduce_margin_by_amount
burnt_debt_shares: uint256 = self._repay(position.debt_token, reduce_debt_by_amount)
position.debt_shares -= burnt_debt_shares
position.position_amount -= _reduce_by_amount
```
