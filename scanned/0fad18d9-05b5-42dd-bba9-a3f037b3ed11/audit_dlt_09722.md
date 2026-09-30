# [?] fix the overflow issue in '_refill'

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2025-01-02
Source: https://github.com/etherfi-protocol/smart-contracts/commit/7a909acc0bffd81da44ded1eeefa0257402c1ed0
Type: security-commit

## Details
fix the overflow issue in '_refill'

Signed-off-by: syko <seongyun@postech.ac.kr>

## Patch
### lib/BucketLimiter.sol
```diff
@@ -109,23 +109,22 @@ library BucketLimiter {
     }
 
     function _refill(Limit memory limit) internal view {
-        // We allow for overflow here, as the delta is resilient against it.
         uint64 now_ = uint64(block.timestamp);
 
         if (now_ == limit.lastRefill) {
             return;
         }
 
-        uint64 delta;
+        uint256 delta;
         unchecked {
             delta = now_ - limit.lastRefill;
         }
-        uint64 tokens = delta * limit.refillRate;
-        uint64 newRemaining = limit.remaining + tokens;
+        uint256 tokens = delta * uint256(limit.refillRate);
+        uint256 newRemaining = uint256(limit.remaining) + tokens;
         if (newRemaining > limit.capacity) {
             limit.remaining = limit.capacity;
         } else {
-            limit.remaining = newRemaining;
+            limit.remaining = uint64(newRemaining);
         }
         limit.lastRefill = now_;
     }
@@ -167,4 +166,4 @@ library BucketLimiter {
         refill(limit);
         limit.remaining = remaining;
     }
-}
\ No newline at end of file
+}
```
