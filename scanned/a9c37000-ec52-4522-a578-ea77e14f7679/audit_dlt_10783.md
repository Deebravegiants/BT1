# [?] core/rawdb: fix panic in freezer (#30973) (#680)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2025-02-12
Source: https://github.com/axieinfinity/ronin-archive/commit/81eef178051abeeb8139d4ee5ecb38d32e004b25
Type: security-commit

## Details
core/rawdb: fix panic in freezer (#30973) (#680)

commit https://github.com/ethereum/go-ethereum/commit/c5a8d3485191d15363b9817da1afcac3fce5ddeb.

Fixes an issue where the node panics when an LStat fails with something
other than os.ErrNotExist

Reported-by: eugenioclrc <eugenioclrc@gmail.com>
Co-authored-by: Marius van der Wijden <m.vanderwijden@live.de>

## Patch
### core/rawdb/freezer.go
```diff
@@ -107,6 +107,10 @@ func newFreezer(datadir string, namespace string, readonly bool, maxTableSize ui
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
