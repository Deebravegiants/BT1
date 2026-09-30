# [?] prevent crash in FindMergeRange (#15278)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-05-27
Source: https://github.com/erigontech/erigon/commit/67f7ac1bafd075c84f1c2795da62bc6537f025d9
Type: security-commit

## Details
prevent crash in FindMergeRange (#15278)

## Patch
### turbo/snapshotsync/merger.go
```diff
@@ -52,7 +52,7 @@ func (m *Merger) FindMergeRanges(currentRanges []Range, maxBlockNum uint64) (toM
 			}
 			aggFrom := r.To() - span
 			toMerge = append(toMerge, NewRange(aggFrom, r.To()))
-			for currentRanges[i].From() > aggFrom {
+			for i >= 0 && currentRanges[i].From() > aggFrom {
 				i--
 			}
 			break
```
