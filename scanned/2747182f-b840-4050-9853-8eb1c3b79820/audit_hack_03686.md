# [H] Only an `owner` should be allowed to `rescueER20` but the modifier is `onlyExecutor()`

## Summary
Severity: High
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L86
Type: audit-issue

## Details
# Only an `owner` should be allowed to `rescueER20` but the modifier is `onlyExecutor()`

## Summary
According to the natspec notes on `rescueER20` [FeeBuyback.sol#L86](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L86) only an `owner` should be allowed to call `rescueER20`
> * @dev Only an owner is allowed to make this function call

## Vulnerability Detail
The current modifier in the `rescueER20` is `onlyExecutor()` that means that an executor can call this function instead of an owner.

## Impact
Only an executor instead of an owner can call `rescueER20`

## Code Snippet
[FeeBuyback.sol#L94](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94)
```solidity
  function rescueERC20(address account, address externalToken, uint256 amount) public onlyExecutor() returns (bool) {
```

## Tool used
Manual Review

## Recommendation
Change `onlyExecutor()` for `onlyOwner()`

```diff
diff --git a/contracts/fee-buyback/FeeBuyback.sol b/contracts/fee-buyback/FeeBuyback.sol
index 86c2234..3475dd1 100644
--- a/contracts/fee-buyback/FeeBuyback.sol
+++ b/contracts/fee-buyback/FeeBuyback.sol
@@ -91,7 +91,7 @@ contract FeeBuyback is IFeeBuyback, TieredOwnership {
   *
   * Emits a {Transfer} event.
   */
-  function rescueERC20(address account, address externalToken, uint256 amount) public onlyExecutor() returns (bool) {
+  function rescueERC20(address account, address externalToken, uint256 amount) public onlyOwner() returns (bool) {
     IERC20(externalToken).transfer(account, amount);
     return true;
   }
```
