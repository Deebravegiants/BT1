# [?] Merge pull request #1236 from lidofinance/fix/setexitdeadlinethreshold-underflow

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2025-07-14
Source: https://github.com/lidofinance/core/commit/5f33c4128c315d32e20b87ab88c09ba6b3c53fbb
Type: security-commit

## Details
Merge pull request #1236 from lidofinance/fix/setexitdeadlinethreshold-underflow

feat: add underflow protection and tests for setExitDeadlineThreshold

## Patch
### contracts/0.4.24/nos/NodeOperatorsRegistry.sol
```diff
@@ -1074,6 +1074,9 @@ contract NodeOperatorsRegistry is AragonApp, Versioned {
     function _setExitDeadlineThreshold(uint256 _threshold, uint256 _lateReportingWindow) internal {
         require(_threshold > 0, "INVALID_EXIT_DELAY_THRESHOLD");
 
+        // Check for underflow protection before computing currentCutoffTimestamp
+        require(block.timestamp >= _threshold + _lateReportingWindow, "CUTOFF_TIMESTAMP_UNDERFLOW");
+
         // Set the cutoff timestamp to the current time minus the threshold and reportingWindow period
         uint256 currentCutoffTimestamp = block.timestamp - _threshold - _lateReportingWindow;
         require(exitPenaltyCutoffTimestamp() <= currentCutoffTimestamp, "INVALID_EXIT_PENALTY_CUTOFF_TIMESTAMP");
```

### test/0.4.24/nor/nor.initialize.upgrade.test.ts
```diff
@@ -202,4 +202,113 @@ describe("NodeOperatorsRegistry.sol:initialize-and-upgrade", () => {
       expect(await nor.exitPenaltyCutoffTimestamp()).to.be.lte(currentTimestamp);
     });
   });
+
+  context("setExitDeadlineThreshold", () => {
+    beforeEach(async () => {
+      locator = await deployLidoLocator({ lido: lido });
+      await nor.initialize(locator, moduleType, 86400n);
+    });
+
+    it("Successfully sets exit deadline threshold with valid parameters", async () => {
+      // Use smaller threshold and reporting window to get a higher (later) cutoff timestamp
+      const threshold = 43200n; // 12 hours (smaller than initial 24h)
+      const reportingWindow = 3600n; // 1 hour
+
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(threshold, reportingWindow))
+        .to.emit(nor, "ExitDeadlineThresholdChanged")
+        .withArgs(threshold, reportingWindow);
+
+      expect(await nor.exitDeadlineThreshold(0)).to.equal(threshold);
+    });
+
+    it("Reverts when threshold is zero", async () => {
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(0n, 3600n))
+        .to.be.revertedWith("INVALID_EXIT_DELAY_THRESHOLD");
+    });
+
+    it("Reverts when sum of threshold and reporting window causes underflow", async () => {
+      const currentTime = await time.latest();
+      const threshold = BigInt(currentTime) + 1000n; // Future timestamp
+      const reportingWindow = 1000n;
+
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(threshold, reportingWindow))
+        .to.be.revertedWith("CUTOFF_TIMESTAMP_UNDERFLOW");
+    });
+
+    it("Reverts when new cutoff timestamp is less than current cutoff timestamp", async () => {
+      // First set a smaller threshold to get a higher cutoff timestamp
+      await nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(43200n, 1800n);
+
+      // Try to set a higher threshold that would result in a lower (earlier) cutoff timestamp
+      // This should fail because cutoff timestamp must be monotonically increasing
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(172800n, 3600n))
+        .to.be.revertedWith("INVALID_EXIT_PENALTY_CUTOFF_TIMESTAMP");
+    });
+
+    it("Works correctly with minimal values", async () => {
+      // Use minimal threshold and no reporting window to get maximum cutoff timestamp
+      const threshold = 1n;
+      const reportingWindow = 0n;
+
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(threshold, reportingWindow))
+        .to.emit(nor, "ExitDeadlineThresholdChanged")
+        .withArgs(threshold, reportingWindow);
+
+      expect(await nor.exitDeadlineThreshold(0)).to.equal(threshold);
+
+      const currentTime = BigInt(await time.latest());
+      const actualCutoff = await nor.exitPenaltyCutoffTimestamp();
+      expect(actualCutoff).to.be.closeTo(currentTime - 1n, 5n);
+    });
+
+    it("Prevents underflow scenario", async () => {
+      // Simulate scenario where _threshold + _lateReportingWindow > block.timestamp
+      const currentTime = BigInt(await time.latest());
+
+      // This should fail due to underflow protection
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(currentTime, currentTime))
+        .to.be.revertedWith("CUTOFF_TIMESTAMP_UNDERFLOW");
+    });
+
+    it("Only allows MANAGE_NODE_OPERATOR_ROLE to set threshold", async () => {
+      await expect(nor.connect(user).setExitDeadlineThreshold(43200n, 3600n))
+        .to.be.revertedWith("APP_AUTH_FAILED");
+    });
+
+    it("Updates cutoff timestamp correctly with monotonic increase", async () => {
+      const initialCutoff = await nor.exitPenaltyCutoffTimestamp();
+
+      // Use smaller threshold to ensure new cutoff timestamp is higher
+      const threshold = 21600n; // 6 hours (smaller than initial 24h)
+      const reportingWindow = 3600n; // 1 hour
+
+      await nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(threshold, reportingWindow);
+
+      const newCutoff = await nor.exitPenaltyCutoffTimestamp();
+
+      // New cutoff should be greater than or equal to the initial cutoff (monotonic)
+      expect(newCutoff).to.be.gte(initialCutoff);
+
+      // Verify the threshold was updated
+      expect(await nor.exitDeadlineThreshold(0)).to.equal(threshold);
+    });
+
+    it("Allows setting same cutoff timestamp", async () => {
+      const currentCutoff = await nor.exitPenaltyCutoffTimestamp();
+
+      // Advance time a bit
+      await time.increase(3600); // 1 hour
+
+      // Calculate parameters that would result in the same cutoff timestamp
+      const newCurrentTime = BigInt(await time.latest());
+      const targetCutoff = currentCutoff;
+      const newThreshold = 43200n; // 12 hours
+      const newReportingWindow = newCurrentTime - targetCutoff - newThreshold;
+
+      // This should work as the cutoff timestamp will be the same (>= condition)
+      await expect(nor.connect(nodeOperatorsManager).setExitDeadlineThreshold(newThreshold, newReportingWindow))
+        .to.emit(nor, "ExitDeadlineThresholdChanged")
+        .withArgs(newThreshold, newReportingWindow);
+    });
+  });
 });
```
