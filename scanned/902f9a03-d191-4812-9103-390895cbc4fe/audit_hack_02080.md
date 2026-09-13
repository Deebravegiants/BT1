# [M] 6.1 Reentrancies

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

```
1.During the execution of remove_liquidity and remove_liquidity_imbalance multiple asset
transfers are made. One of these assets is ETH, while the others are ERC-20 tokens. The transfer
of ETH can lead to the following reentrancy. Through the transfer of ETH, the execution might
reenter the contract and call donate_admin_fees. Note that this requires owner privileges. Inside
donate_admin_fees, the internal balances mapping for the ERC-20 tokens will be updated as
follows:
```
```
self.balances[i] = ERC20(coin).balanceOf(self)
```
```
This assignment is incorrect in this context as the contract still holds the tokens that are about to be
transferred due to the removed liquidity. Hence, after the transaction is complete:
self.balances[i] > ERC20(coin).balanceOf(self). This breaks an important invariant in
the contract.
2.During the call to withdraw_admin_fees an ETH transfer takes place. The transfer of ETH can
lead to the following reentrancy. Through the transfer of ETH, the execution might reenter the
contract and call donate_admin_fees. Note that this requires owner privileges, but these were
already needed for withdraw_admin_fees. As a result, the admin fees for some of the coins will
be donated while the admin fees for other coins will be withdrawn, leading to a state that is only
reachable through a reentrancy.
3.Certain admin functions have no reentrancy protection. Hence, they can be called in a reentrancy
from any of the functions that transfers ETH. However, for those reentrancies the only effects are
incorrectly ordered events. As an example, a NewFee event could be emitted in between multiple
events belonging to a remove_liquidity call.
```
Code corrected: Additional Reentrancy Guards were added. These now also cover the functions
donate_admin_fees and apply_new_fee among others.
