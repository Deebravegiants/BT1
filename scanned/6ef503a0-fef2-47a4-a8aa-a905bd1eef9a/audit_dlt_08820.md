# [?] fix(protocol): prevent quota issuance overflow in QuotaManager (#21841)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-06-23
Source: https://github.com/taikoxyz/taiko-mono/commit/f3f429593e1cfa7df7f285e6be51694bdabd9da6
Type: security-commit

## Details
fix(protocol): prevent quota issuance overflow in QuotaManager (#21841)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### packages/protocol/contracts/shared/bridge/QuotaManager.sol
```diff
@@ -81,14 +81,27 @@ contract QuotaManager is Ownable2Step, IQuotaManager {
 
     /// @notice Returns the available quota for a given token.
     /// @param _token The token address with Ether represented by address(0).
-    /// @param _leap Amount of seconds in the future.
+    /// @param _leap Number of seconds in the future to look ahead. Values greater than or equal
+    /// to `quotaPeriod` are treated as a full period (the quota is fully restored), so arbitrarily
+    /// large values are safe and never overflow.
     /// @return The available quota.
     function availableQuota(address _token, uint256 _leap) public view returns (uint256) {
         Quota memory q = tokenQuota[_token];
         if (q.quota == 0) return UNLIMITED_QUOTA;
         if (q.updatedAt == 0) return q.quota;
 
-        uint256 issuance = q.quota * (block.timestamp + _leap - q.updatedAt) / quotaPeriod;
+        // Cap the elapsed time at `quotaPeriod`: once a full period has passed the quota is
+        // fully restored, so a larger elapsed value would not change the result (it is capped
+        // at `q.quota` below anyway). A `_leap` of at least `quotaPeriod` already implies full
+        // restoration, so it is short-circuited; this also avoids overflowing `block.timestamp +
+        // _leap` for extreme caller-supplied lookahead values. Capping `elapsed` bounds the
+        // multiplication to `q.quota * quotaPeriod`, which can never overflow uint256, so
+        // `consumeQuota` keeps working even though `block.timestamp - q.updatedAt` grows without
+        // bound.
+        uint256 elapsed = _leap >= quotaPeriod
+            ? quotaPeriod
+            : (block.timestamp + _leap - q.updatedAt).min(quotaPeriod);
+        uint256 issuance = q.quota * elapsed / quotaPeriod;
         return (issuance + q.available).min(q.quota);
     }
 
```

### packages/protocol/test/shared/bridge/QuotaManager.t.sol
```diff
@@ -85,6 +85,62 @@ contract TestQuotaManager is CommonTest {
         assertEq(qm.availableQuota(Ether, 0), 4 ether);
     }
 
+    function test_quota_manager_restores_fully_after_long_period() public {
+        address Ether = address(0);
+
+        vm.prank(deployer);
+        qm.updateQuota(Ether, 10 ether);
+
+        vm.prank(bridge);
+        qm.consumeQuota(Ether, 6 ether);
+        assertEq(qm.availableQuota(Ether, 0), 4 ether);
+
+        // Warp far beyond a single quota period (~100 years). The quota must be fully restored
+        // and capped at the configured quota, and consumeQuota must keep working.
+        vm.warp(block.timestamp + 36_500 days);
+        assertEq(qm.availableQuota(Ether, 0), 10 ether);
+
+        vm.prank(bridge);
+        qm.consumeQuota(Ether, 10 ether);
+        assertEq(qm.availableQuota(Ether, 0), 0);
+    }
+
+    function test_quota_manager_no_overflow_with_max_quota_and_large_elapsed() public {
+        address Ether = address(0);
+
+        // Configure the maximum possible quota to maximize the overflow risk in the issuance
+        // calculation `q.quota * elapsed`.
+        vm.prank(deployer);
+        qm.updateQuota(Ether, type(uint104).max);
+
+        // Consume a tiny amount so that `updatedAt` becomes non-zero and the issuance branch
+        // (rather than the early `q.updatedAt == 0` return) is exercised.
+        vm.prank(bridge);
+        qm.consumeQuota(Ether, 1);
+
+        // With an unbounded elapsed time, `q.quota * elapsed` would exceed uint256 and revert,
+        // bricking `consumeQuota`. Capping elapsed at `quotaPeriod` keeps it safe and simply
+        // returns the fully restored quota. `2 ** 160` is large enough to overflow the product
+        // while keeping `block.timestamp + _leap` itself within uint256.
+        uint256 hugeLeap = 1 << 160;
+        assertEq(qm.availableQuota(Ether, hugeLeap), type(uint104).max);
+    }
+
+    function test_quota_manager_no_overflow_with_max_leap() public {
+        address Ether = address(0);
+
+        vm.prank(deployer);
+        qm.updateQuota(Ether, type(uint104).max);
+
+        // Set a non-zero `updatedAt` so the issuance branch (not the early return) is taken.
+        vm.prank(bridge);
+        qm.consumeQuota(Ether, 1);
+
+        // A `_leap` near uint256 max must not overflow the `block.timestamp + _leap` addition.
+        // The lookahead saturates at `quotaPeriod`, so the fully restored quota is reported.
+        assertEq(qm.availableQuota(Ether, type(uint256).max), type(uint104).max);
+    }
+
     function test_calc_quota() public pure {
         uint24 quotaPeriod = 24 hours;
         uint104 value = 4_000_000; // USD
```
