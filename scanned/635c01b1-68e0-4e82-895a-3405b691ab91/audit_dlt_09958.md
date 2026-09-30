# [?] Merge pull request #1500 from lidofinance/fix/no-fees-overflow

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2025-10-07
Source: https://github.com/lidofinance/core/commit/8f8b86a7f58a8dd73fd15529808506f79ec62ae1
Type: security-commit

## Details
Merge pull request #1500 from lidofinance/fix/no-fees-overflow

fix: overflow in node operator fee

## Patch
### contracts/0.8.25/vaults/dashboard/NodeOperatorFee.sol
```diff
@@ -318,16 +318,18 @@ contract NodeOperatorFee is Permissions {
      * @dev fee exemption can only be positive
      */
     function _addFeeExemption(uint256 _amount) internal {
-        _correctSettledGrowth(settledGrowth + _amount.toInt256());
+        if (_amount > type(uint104).max) revert UnexpectedFeeExemptionAmount();
+
+        _correctSettledGrowth(settledGrowth + int256(_amount));
     }
 
     function _calculateFee() internal view returns (uint256 fee, int128 growth) {
         VaultHub.Report memory report = latestReport();
-        growth = int128(int256(uint256(report.totalValue))) - int128(report.inOutDelta);
-        int128 unsettledGrowth = growth - settledGrowth;
+        growth = int128(uint128(report.totalValue)) - int128(report.inOutDelta);
+        int256 unsettledGrowth = growth - settledGrowth;
 
         if (unsettledGrowth > 0) {
-            fee = (uint256(uint128(unsettledGrowth)) * uint256(feeRate)) / TOTAL_BASIS_POINTS;
+            fee = (uint256(unsettledGrowth) * feeRate) / TOTAL_BASIS_POINTS;
         }
     }
 
@@ -424,6 +426,11 @@ contract NodeOperatorFee is Permissions {
      */
     error UnexpectedSettledGrowth();
 
+    /**
+     * @dev Error emitted when the fee exemption amount does not match the expected value
+     */
+    error UnexpectedFeeExemptionAmount();
+
     /**
      * @dev Error emitted when the settled growth is pending manual adjustment.
      */
```

### test/0.8.25/vaults/nodeOperatorFee/nodeOperatorFee.test.ts
```diff
@@ -377,6 +377,12 @@ describe("NodeOperatorFee.sol", () => {
       );
     });
 
+    it("reverts if the amount is too large", async () => {
+      await expect(
+        nodeOperatorFee.connect(nodeOperatorFeeExempter).addFeeExemption(2n ** 104n + 1n),
+      ).to.be.revertedWithCustomError(nodeOperatorFee, "UnexpectedFeeExemptionAmount");
+    });
+
     it("adjuster can addFeeExemption", async () => {
       const increase = ether("10");
 
```
