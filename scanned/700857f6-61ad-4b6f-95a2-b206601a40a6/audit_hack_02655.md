# [M] `Queue` can be drained of its collateral if collateral is a fee-on-transfer token

## Summary
Severity: Medium
Reporter: joestakey
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L104
Type: audit-issue

## Details
# `Queue` can be drained of its collateral if collateral is a fee-on-transfer token

## Summary
Because of the way `Queue.deposit()` and `Queue.cancel()` handle the transfer of collateral, `Queue` can be drained if the collateral used has a fee-on-transfer.

## Vulnerability Detail
The deposit system in `Queue` is designed to `mint claim tokens 1:1 with collateral deposited`.

Let us show the example of a vault with a fee-on-transfer token, say with a fee of 1%.
We assume `Queue` has a token balance of `1000` collateral Tokens.

1- Alice calls `Queue.deposit(amount = 100 collateral Tokens)`. Because the token has a fee upon transfer, `Queue` only receives 99 collateral tokens.
The [deposit](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L104) call mints `100` claim tokens to Alice.
2- Alice calls `Queue.cancel(amount = 100 claim Tokens)`, which burns Alice's claim tokens, and then transfers `100` collateral Tokens from the vault, sending `99` to Alice.

`Queue` has now a balance of `999` collateral Tokens.

## Impact
The attack is not profitable to the attacker as it has a `1:1` cost - Alice needs to spend `X` tokens to reduce the `Queue` balance of `X` tokens, but the key takeaway here is that the **1:1 Claim Token to Collateral ratio in `Queue` is broken**.
It can technically be used to drain the Queue of its collateral - especially if several users decided to launch a joined attack, spreading the cost of the attack.

## Code Snippet

## Tool used
Manual Review

## Recommendation
In `Queue.deposit()`, call `_deposit` with the balance difference of the contract rather than `amount`

```diff
+            uint256 balanceBefore = ERC20.balanceOf(address(this));
103:         ERC20.safeTransferFrom(msg.sender, address(this), amount - credited);
+            uint256 balanceAfter = ERC20.balanceOf(address(this));
+104:        _deposit(l, balanceAfter - balanceBefore);
-104:        _deposit(l, amount);
```

You can also state that fee-on-transfers `ERC20` tokens are not supported as collateral. It is worth keeping in mind that some tokens (like `USDT`) have transfer fees that are currently zero but may be set to a non-zero value in the future.
