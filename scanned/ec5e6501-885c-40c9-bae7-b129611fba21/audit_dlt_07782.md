# [?] paranoid underflow protection without error handling (#14044)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2024-05-23
Source: https://github.com/OffchainLabs/prysm/commit/62b5c43d876d31a35040d0a29d6d6bbfd6467b22
Type: security-commit

## Details
paranoid underflow protection without error handling (#14044)

Co-authored-by: Kasey Kirkham <kasey@users.noreply.github.com>

## Patch
### beacon-chain/sync/initial-sync/blocks_fetcher.go
```diff
@@ -461,7 +461,7 @@ func (r *blobRange) Request() *p2ppb.BlobSidecarsByRangeRequest {
 	}
 	return &p2ppb.BlobSidecarsByRangeRequest{
 		StartSlot: r.low,
-		Count:     uint64(r.high.SubSlot(r.low)) + 1,
+		Count:     uint64(r.high.FlooredSubSlot(r.low)) + 1,
 	}
 }
 
```

### consensus-types/primitives/slot.go
```diff
@@ -124,6 +124,14 @@ func (s Slot) SubSlot(x Slot) Slot {
 	return s.Sub(uint64(x))
 }
 
+// FlooredSubSlot safely subtracts x from the slot, returning 0 if the result would underflow.
+func (s Slot) FlooredSubSlot(x Slot) Slot {
+	if s < x {
+		return 0
+	}
+	return s - x
+}
+
 // SafeSubSlot finds difference between two slot values.
 // In case of arithmetic issues (overflow/underflow/div by zero) error is returned.
 func (s Slot) SafeSubSlot(x Slot) (Slot, error) {
```
