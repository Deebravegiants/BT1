# [?] Merge pull request #10569 from filecoin-project/fix/panic-index-oor

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-03-27
Source: https://github.com/filecoin-project/lotus/commit/2120fae2b6096b5bd27630ede280aa9b36510ed9
Type: security-commit

## Details
Merge pull request #10569 from filecoin-project/fix/panic-index-oor

fix: proving: Initialize slice with with same length as partition

## Patch
### cmd/lotus-miner/proving.go
```diff
@@ -658,6 +658,10 @@ It will not send any messages to the chain.`,
 		for _, i := range res {
 			var postParam SubmitWindowedPoStParams
 			postParam.Deadline = i.Deadline
+
+			// Initialize the postParam.Partitions slice with the same length as i.Partitions
+			postParam.Partitions = make([]PoStPartition, len(i.Partitions))
+
 			for id, part := range i.Partitions {
 				postParam.Partitions[id].Index = part.Index
 				count, err := part.Skipped.Count()
```
