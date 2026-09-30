# [?] fix(coordinator): panic (#1407)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2024-06-28
Source: https://github.com/scroll-tech/scroll/commit/a2536d56139c979124cd6709e52787943661ad7a
Type: security-commit

## Details
fix(coordinator): panic (#1407)

Co-authored-by: colinlyguo <colinlyguo@users.noreply.github.com>

## Patch
### common/version/version.go
```diff
@@ -5,7 +5,7 @@ import (
 	"runtime/debug"
 )
 
-var tag = "v4.4.21"
+var tag = "v4.4.22"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### coordinator/internal/logic/provertask/batch_prover_task.go
```diff
@@ -263,7 +263,7 @@ func (bp *BatchProverTask) assignWithTwoCircuits(ctx *gin.Context, taskCtx *prov
 	var hardForkName string
 	getHardForkName := func(batch *orm.Batch) (string, error) {
 		for i := 0; i < 2; i++ {
-			if chunkRanges[i].contains(batch.StartChunkIndex, batch.EndChunkIndex) {
+			if chunkRanges[i] != nil && chunkRanges[i].contains(batch.StartChunkIndex, batch.EndChunkIndex) {
 				hardForkName = hardForkNames[i]
 				break
 			}
```
