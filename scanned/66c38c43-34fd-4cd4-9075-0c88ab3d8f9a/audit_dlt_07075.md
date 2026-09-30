# [?] integration: fix panic in rebuild commitment when datadir name contains commitment (#17749)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-03
Source: https://github.com/erigontech/erigon/commit/dd8149804fcf12aa11ac6bf05dbc588eb8b82f60
Type: security-commit

## Details
integration: fix panic in rebuild commitment when datadir name contains commitment (#17749)

this PR fixes a nil panic I got because my datadir name contained
"commitment" and that messed up file filtering when calling
`checkCommitmentFileHasRoot` (it got called for an accounts file)

datadir: `~/erigon-data/e3-caplin-chiado-full-rebuild-commitment`
panic:
```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x2 addr=0x18 pc=0x1040d1488]

goroutine 1 [running]:
github.com/erigontech/erigon/db/state.(*Cursor).Key(...)
found state key with kvi /Users/taratorio/erigon-data/e3-caplin-chiado-full-rebuild-commitment/snapshots/domain/v2.0-rcache.0-32.kv
found state key with kvi /Users/taratorio/erigon-data/e3-caplin-chiado-full-rebuild-commitment/snapshots/domain/v2.0-rcache.32-36.kv
    /Users/taratorio/erigon3-run/db/state/btree_index.go:84
github.com/erigontech/erigon/cmd/utils/app.checkCommitmentFileHasRoot({0x14002b861c0, 0x6b})
    /Users/taratorio/erigon3-run/cmd/utils/app/snapshots_cmd.go:497 +0x638
github.com/erigontech/erigon/cmd/utils/app.DeleteStateSnapshots({{0x16d8fb62f, 0x45}, {0x16d8fb62f, 0x45}, {0x4401ff166e0, 0x4f}, {0x4401ff16730, 0x4a}, {0x4401ff16780, 0x4f}, ...}, ...)
    /Users/taratorio/erigon3-run/cmd/utils/app/snapshots_cmd.go:560 +0x324
github.com/erigontech/erigon/cmd/integration/commands.commitmentRebuild({0x10563a790, 0x44030d32c90}, {0x1056105c8, 0x14000698eb0}, {0x10562b610, 0x14000464140})
```

## Patch
### cmd/utils/app/snapshots_cmd.go
```diff
@@ -556,7 +556,7 @@ func DeleteStateSnapshots(dirs datadir.Dirs, removeLatest, promptUserBeforeDelet
 
 		// check that commitment file has state in it
 		// When domains are "compacted", we want to keep latest commitment file with state key in it
-		if doesRmCommitment && strings.Contains(res.Path, "commitment") && strings.HasSuffix(res.Path, ".kv") {
+		if doesRmCommitment && strings.Contains(filepath.Base(res.Path), "commitment") && strings.HasSuffix(res.Path, ".kv") {
 			hasState, broken, err := checkCommitmentFileHasRoot(res.Path)
 			if err != nil {
 				return err
```
