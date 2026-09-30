# [?] Fix integer overflow (#10222)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-02-10
Source: https://github.com/OffchainLabs/prysm/commit/72a2dd004be85f30305ce756b6ba761c85f3da3e
Type: security-commit

## Details
Fix integer overflow (#10222)

Co-authored-by: terence tsao <terence@prysmaticlabs.com>

## Patch
### beacon-chain/forkchoice/protoarray/store.go
```diff
@@ -451,21 +451,15 @@ func (s *Store) applyWeightChanges(
 		}
 		s.proposerBoostLock.Unlock()
 
+		// A node's weight can not be negative but the delta can be negative.
 		if nodeDelta < 0 {
-			// A node's weight can not be negative but the delta can be negative.
-			if int(n.weight)+nodeDelta < 0 {
+			d := uint64(-nodeDelta)
+			if n.weight < d {
 				n.weight = 0
 			} else {
-				// Absolute value of node delta.
-				d := nodeDelta
-				if nodeDelta < 0 {
-					d *= -1
-				}
-				// Subtract node's weight.
-				n.weight -= uint64(d)
+				n.weight -= d
 			}
 		} else {
-			// Add node's weight.
 			n.weight += uint64(nodeDelta)
 		}
 
```
