# [?] Merge pull request #9141 from filecoin-project/fix/getcommitcutoff-panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-08-09
Source: https://github.com/filecoin-project/lotus/commit/533f1a6fdbba2bc83556a8f493ac5e30dffa955d
Type: security-commit

## Details
Merge pull request #9141 from filecoin-project/fix/getcommitcutoff-panic

fix: storage: don't panic in getCommitCutoff when precommit is not found

## Patch
### storage/pipeline/commit_batch.go
```diff
@@ -573,6 +573,9 @@ func (b *CommitBatcher) getCommitCutoff(si SectorInfo) (time.Time, error) {
 		log.Errorf("getting precommit info: %s", err)
 		return time.Now(), err
 	}
+	if pci == nil {
+		return time.Now(), xerrors.Errorf("precommit info not found")
+	}
 	av, err := actors.VersionForNetwork(nv)
 	if err != nil {
 		log.Errorf("unsupported network vrsion: %s", err)
```
