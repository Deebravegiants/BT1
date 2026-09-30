# [?] Merge pull request #9703 from filecoin-project/asr/fix-panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-11-22
Source: https://github.com/filecoin-project/lotus/commit/70dc920f8c04d9eae5fdfff11a55104c4e67739b
Type: security-commit

## Details
Merge pull request #9703 from filecoin-project/asr/fix-panic

fix: cli: check found before dereferencing SectorInfo

## Patch
### cmd/lotus-miner/sectors.go
```diff
@@ -919,12 +919,12 @@ var sectorsRenewCmd = &cli.Command{
 				}
 
 				si, found := activeSectorsInfo[abi.SectorNumber(id)]
-				if len(si.DealIDs) > 0 && cctx.Bool("only-cc") {
-					continue
-				}
 				if !found {
 					return xerrors.Errorf("sector %d is not active", id)
 				}
+				if len(si.DealIDs) > 0 && cctx.Bool("only-cc") {
+					continue
+				}
 
 				sis = append(sis, si)
 			}
```
