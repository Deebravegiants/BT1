# [?] core/rawdb: fix panic in freezer (#30973)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-01-06
Source: https://github.com/ethereum/go-ethereum/commit/c5a8d3485191d15363b9817da1afcac3fce5ddeb
Type: security-commit

## Details
core/rawdb: fix panic in freezer (#30973)

Fixes an issue where the node panics when an LStat fails with something 
other than os.ErrNotExist

closes https://github.com/ethereum/go-ethereum/issues/30968

## Patch
### core/rawdb/freezer.go
```diff
@@ -87,6 +87,10 @@ func NewFreezer(datadir string, namespace string, readonly bool, maxTableSize ui
 	)
 	// Ensure the datadir is not a symbolic link if it exists.
 	if info, err := os.Lstat(datadir); !os.IsNotExist(err) {
+		if info == nil {
+			log.Warn("Could not Lstat the database", "path", datadir)
+			return nil, errors.New("lstat failed")
+		}
 		if info.Mode()&os.ModeSymlink != 0 {
 			log.Warn("Symbolic link ancient database is not supported", "path", datadir)
 			return nil, errSymlinkDatadir
```
