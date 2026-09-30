# [?] fix nil panic error

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-05-22
Source: https://github.com/cometbft/cometbft/commit/118b86b1ef78bd43d0a03dc663eac3b3516cc80c
Type: security-commit

## Details
fix nil panic error

msg is nil and if we continue executing, we'll get nil exception at
`msg.Msg.(....)`

## Patch
### consensus/wal.go
```diff
@@ -144,8 +144,8 @@ type WALSearchOptions struct {
 	IgnoreDataCorruptionErrors bool
 }
 
-// SearchForEndHeight searches for the EndHeightMessage with the height and
-// returns an auto.GroupReader, whenever it was found or not and an error.
+// SearchForEndHeight searches for the EndHeightMessage with the given height
+// and returns an auto.GroupReader, whenever it was found or not and an error.
 // Group reader will be nil if found equals false.
 //
 // CONTRACT: caller must close group reader.
@@ -170,7 +170,9 @@ func (wal *baseWAL) SearchForEndHeight(height int64, options *WALSearchOptions)
 				break
 			}
 			if options.IgnoreDataCorruptionErrors && IsDataCorruptionError(err) {
+				wal.Logger.Debug("Corrupted entry. Skipping...", "err", err)
 				// do nothing
+				continue
 			} else if err != nil {
 				gr.Close()
 				return nil, false, err
```
