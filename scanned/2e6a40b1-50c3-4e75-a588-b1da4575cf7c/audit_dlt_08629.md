# [?] Merge pull request #9232 from filecoin-project/fix/gatewaytest-panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-08-29
Source: https://github.com/filecoin-project/lotus/commit/25323001564917c644ba8b522783b705106af971
Type: security-commit

## Details
Merge pull request #9232 from filecoin-project/fix/gatewaytest-panic

cli: Don't panic with no providers in client retrieve

## Patch
### cli/client_retr.go
```diff
@@ -315,6 +315,9 @@ Examples:
 		if err != nil {
 			return err
 		}
+		if eref == nil {
+			return xerrors.Errorf("failed to find providers")
+		}
 
 		if s != nil {
 			eref.DAGs = append(eref.DAGs, lapi.DagSpec{DataSelector: s, ExportMerkleProof: cctx.Bool("car-export-merkle-proof")})
```
