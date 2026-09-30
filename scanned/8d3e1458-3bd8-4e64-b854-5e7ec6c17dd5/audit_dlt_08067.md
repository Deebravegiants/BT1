# [?] p2p/discover: fix out-of-bounds issue

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-02-13
Source: https://github.com/celo-org/celo-blockchain/commit/20797348ca9d037dc5b7a830bafdfe1ea703eac0
Type: security-commit

## Details
p2p/discover: fix out-of-bounds issue

## Patch
### p2p/discover/table.go
```diff
@@ -763,7 +763,7 @@ func (tab *Table) addReplacement(b *bucket, n *Node) {
 // last entry in the bucket. If 'last' isn't the last entry, it has either been replaced
 // with someone else or became active.
 func (tab *Table) replace(b *bucket, last *Node) *Node {
-	if len(b.entries) >= 0 && b.entries[len(b.entries)-1].ID != last.ID {
+	if len(b.entries) == 0 || b.entries[len(b.entries)-1].ID != last.ID {
 		// Entry has moved, don't replace it.
 		return nil
 	}
```
