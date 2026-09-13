# [M] `approve(<SPENDER>, 0)` before `approve(<SPENDER>, <AMOUNT>)`

## Summary
Severity: Medium
Reporter: rotcivegaf
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47-L82
Type: audit-issue

## Details
# `approve(<SPENDER>, 0)` before `approve(<SPENDER>, <AMOUNT>)`

## Summary

It is recommended reducing the spender `allowance` to zero before each make an `approve(<SPENDER>, <AMOUNT>)` call

## Vulnerability Detail

In the function [`submit`](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47-L82) the parameter `token` could be USDT for example who need reducing the spender `allowance` to zero, look approve of [L72](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L72)
Another case would be that the behavior of [`_telcoin`](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L23) was like that of USDT, look approve of [L63](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L63) and [L79](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L79)

## Impact

Some tokens, like USDT, require first reducing the spender `allowance` to zero, otherwise the transaction will revert

## Code Snippet

```solidity
File: contracts/fee-buyback/FeeBuyback.sol

/// @audit: Only if ERC20 `_telcoin` is known can this be avoided, and should not be exchanged for another token
63      _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));

72      IERC20(token).approve(_aggregator, amount);

/// @audit: Only if ERC20 `_telcoin` is known can this be avoided, and should not be exchanged for another token
79    _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
```

## Tool used

Manual Review

## Recommendation

Use `approve(<SPENDER>, 0)` to set the allowance to zero immediately before each of the existing `approve(<SPENDER>, <AMOUNT>)` call

```diff
File: contracts/fee-buyback/FeeBuyback.sol

@@ -60,6 +60,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //do simple transfer from and submit
     if (token == address(_telcoin)) {
       _telcoin.transferFrom(_safe, address(this), amount);
+      _telcoin.approve(address(_referral), 0);
       _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
       require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
       return true;

@@ -69,6 +70,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //ERC20s only
     if (token != MATIC) {
       IERC20(token).transferFrom(_safe, address(this), amount);
+      IERC20(token).approve(_aggregator, 0);
       IERC20(token).approve(_aggregator, amount);
     }
 
@@ -76,6 +78,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //do simple transfer from and submit
     (bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
     require(swapResult, "FeeBuyback: swap transaction failed");
+    _telcoin.approve(address(_referral), 0);
     _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
     require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
     return true;
```
