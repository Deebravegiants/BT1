# [?] Fix Bandwith Limiter Panic (#11988)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-02-14
Source: https://github.com/OffchainLabs/prysm/commit/449d767294d19529844aabdb1e4d37b6950609f4
Type: security-commit

## Details
Fix Bandwith Limiter Panic (#11988)

## Patch
### beacon-chain/sync/initial-sync/blocks_fetcher.go
```diff
@@ -396,6 +396,12 @@ func timeToWait(wanted, rem, capacity int64, timeTillEmpty time.Duration) time.D
 	if rem >= wanted {
 		return 0
 	}
+	// Handle edge case where capacity is equal to the remaining amount
+	// of blocks. This also handles the impossible case in where remaining blocks
+	// exceed the limiter's capacity.
+	if capacity <= rem {
+		return 0
+	}
 	blocksNeeded := wanted - rem
 	currentNumBlks := capacity - rem
 	expectedTime := int64(timeTillEmpty) * blocksNeeded / currentNumBlks
```

### beacon-chain/sync/initial-sync/blocks_fetcher_test.go
```diff
@@ -914,6 +914,14 @@ func TestTimeToWait(t *testing.T) {
 			timeTillEmpty: 200 * time.Second,
 			want:          0 * time.Second,
 		},
+		{
+			name:          "Limiter has full capacity remaining",
+			wanted:        350,
+			rem:           320,
+			capacity:      320,
+			timeTillEmpty: 0 * time.Second,
+			want:          0 * time.Second,
+		},
 		{
 			name:          "Limiter has reached full capacity",
 			wanted:        64,
```
