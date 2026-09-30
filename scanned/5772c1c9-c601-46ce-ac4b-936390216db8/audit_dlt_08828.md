# [?] fix(protocol): Deposit ether reentrancy (TKO-14) (#15569)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2024-01-25
Source: https://github.com/taikoxyz/taiko-mono/commit/7327ff0dcd4dcdbcb94681332aad8c30a2ec14e1
Type: security-commit

## Details
fix(protocol): Deposit ether reentrancy (TKO-14) (#15569)

Co-authored-by: Keszey Dániel <keszeyd@MacBook-Pro.local>

## Patch
### packages/protocol/contracts/L1/TaikoL1.sol
```diff
@@ -122,7 +122,7 @@ contract TaikoL1 is
     /// @notice Deposits Ether to Layer 2.
     /// @param recipient Address of the recipient for the deposited Ether on
     /// Layer 2.
-    function depositEtherToL2(address recipient) external payable whenNotPaused {
+    function depositEtherToL2(address recipient) external payable nonReentrant whenNotPaused {
         LibDepositing.depositEtherToL2(state, getConfig(), AddressResolver(this), recipient);
     }
 
```
