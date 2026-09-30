# [?] fix: f3 gen power command being non-deterministic (#12764)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-12-05
Source: https://github.com/filecoin-project/lotus/commit/b37410b4673bf4509271587dbcfed31eb7f13dbf
Type: security-commit

## Details
fix: f3 gen power command being non-deterministic (#12764)

Sort the power table before Selecting from it.

## Patch
### cmd/lotus-shed/f3.go
```diff
@@ -170,6 +170,7 @@ var f3GenExplicitPower = &cli.Command{
 			for _, pe := range powerMap {
 				powerList = append(powerList, pe)
 			}
+			sort.Sort(powerList)
 			rng.Shuffle(len(powerList), powerList.Swap)
 
 			iteration := cctx.Int("iteration")
```
