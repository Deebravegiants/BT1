# [M] Missing `deadline` check on `swap` in `SwapRouter`

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L92
Type: audit-issue

## Details
# Missing `deadline` check on `swap` in `SwapRouter`

## Summary

`swap` method should include a `deadline`, that should be used In the `_direct_swap` and `_multi_hop_swap` methods. 

The missing `deadline`, replace by a `block.timestamp` could allow for pending transactions to be maliciously executed at an unfavorable time, potentially leading to bad trades for users. This issue could also be maliciously exploited through Miner Extractable Value (MEV).

## Vulnerability Detail

In the methods _direct_swap and _multi_hop_swap, a transaction deadline is defined in the params dictionary (ExactInputSingleParams and ExactInputParams respectively). However, no validation is done to check if the current block timestamp (block.timestamp) is before the deadline. Without this validation, a transaction could be included in a block after its deadline, potentially leading to unfavorable outcomes for users due to price slippage. Moreover, this issue can be used for MEV where miners choose to include or exclude certain transactions based on profitability.

## Impact

This vulnerability poses a financial risk to the users interacting with the contract, as their transactions may not be executed at the expected time, leading to potential losses due to unfavorable market conditions. It also undermines the fair transaction ordering assumption of the blockchain, as it enables miners to take advantage of the MEV potential.

## Code Snippet

- [SwapRouter.vy#L92](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L92)
- [SwapRouter.vy#L115](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L115)

## Tool used

Manual Review

## Recommendation

Add a `deadline`
```diff
diff --git a/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy b/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy
index 4e53386..5126c2b 100644
--- a/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy
+++ b/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy
@@ -63,14 +63,15 @@ def swap(
     _token_out: address,
     _amount_in: uint256,
     _min_amount_out: uint256,
+    _deadline: uint256,
 ) -> uint256:
     ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
     ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
 
     if self.direct_route[_token_in][_token_out] != 0:
-        return self._direct_swap(_token_in, _token_out, _amount_in, _min_amount_out)
+        return self._direct_swap(_token_in, _token_out, _amount_in, _min_amount_out, _deadline)
     else:
-        return self._multi_hop_swap(_token_in, _token_out, _amount_in, _min_amount_out)
+        return self._multi_hop_swap(_token_in, _token_out, _amount_in, _min_amount_out, _deadline)
 
 
 @internal
@@ -79,6 +80,7 @@ def _direct_swap(
     _token_out: address,
     _amount_in: uint256,
     _min_amount_out: uint256,
+    _deadline: uint256,
 ) -> uint256:
     fee: uint24 = self.direct_route[_token_in][_token_out]
     assert fee != 0, "no direct route"
@@ -89,7 +91,7 @@ def _direct_swap(
             tokenOut: _token_out,
             fee: fee,
             recipient: msg.sender,
-            deadline: block.timestamp,
+            deadline: _deadline,
             amountIn: _amount_in,
             amountOutMinimum: _min_amount_out,
             sqrtPriceLimitX96: 0,
@@ -104,6 +106,7 @@ def _multi_hop_swap(
     _token_out: address,
     _amount_in: uint256,
     _min_amount_out: uint256,
+    _deadline: uint256,
 ) -> uint256:
     path: Bytes[66] = self.paths[_token_in][_token_out]
     assert path != empty(Bytes[66]), "no path configured"
@@ -112,7 +115,7 @@ def _multi_hop_swap(
         {
             path: path,
             recipient: msg.sender,
-            deadline: block.timestamp,
+            deadline: _deadline,
             amountIn: _amount_in,
             amountOutMinimum: _min_amount_out,
         }
```
