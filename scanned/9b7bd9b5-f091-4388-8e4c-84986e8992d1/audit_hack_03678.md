# [H] Missing `approve(0)` before approve

## Summary
Severity: High
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L63
Type: audit-issue

## Details
# Missing `approve(0)` before approve

## Summary
There are 3 instances where the `IERC20.approve()` function is called only once without setting the allowance to zero. Some tokens, like USDT, require first reducing the address' allowance to zero by calling `approve(_spender, 0)`. Transactions will revert when using an unsupported token like USDT (see the approve() function requirement [at line 199](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code)).

## Vulnerability Detail
Some tokens, like USDT, require first reducing the address' allowance to zero by calling `approve(_spender, 0)`. Transactions will revert when using an unsupported token like USDT

## Impact
Transactions will revert when using an unsupported token like USDT

## Code Snippet
[fee-buyback/FeeBuyback.sol#L63](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L63)
[fee-buyback/FeeBuyback.sol#L72](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L72)
[fee-buyback/FeeBuyback.sol#L79](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L79)

## Tool used
Manual Review

## Recommendation
Add an `approve(0)` before approving;
```diff
diff --git a/contracts/fee-buyback/FeeBuyback.sol b/contracts/fee-buyback/FeeBuyback.sol
index 86c2234..e0cb0ca 100644
--- a/contracts/fee-buyback/FeeBuyback.sol
+++ b/contracts/fee-buyback/FeeBuyback.sol
@@ -60,6 +60,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //do simple transfer from and submit
     if (token == address(_telcoin)) {
       _telcoin.transferFrom(_safe, address(this), amount);
+      _telcoin.approve(0);
       _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
       require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
       return true;
@@ -69,6 +70,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //ERC20s only
     if (token != MATIC) {
       IERC20(token).transferFrom(_safe, address(this), amount);
+      IERC20(token).approve(0);
       IERC20(token).approve(_aggregator, amount);
     }
 
@@ -76,6 +78,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
     //do simple transfer from and submit
     (bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
     require(swapResult, "FeeBuyback: swap transaction failed");
+    _telcoin.approve(0);
     _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
     require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
     return true;
```
