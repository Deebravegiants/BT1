# [?] Fix nil info.Length panic (#15460)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-06-05
Source: https://github.com/erigontech/erigon/commit/fa8df0294417d55dc5d6a19c59df8dad0d8f901a
Type: security-commit

## Details
Fix nil info.Length panic (#15460)

Fixes https://github.com/erigontech/erigon/issues/15456

---------

Co-authored-by: antonis19 <antonis19@users.noreply.github.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

## Patch
### erigon-lib/downloader/downloader.go
```diff
@@ -2643,9 +2643,16 @@ func (d *Downloader) addTorrentFilesFromDisk(quiet bool) error {
 		if info, err := d.torrentInfo(ts.DisplayName); err == nil {
 			if info.Completed != nil {
 				fi, serr := os.Stat(filepath.Join(d.SnapDir(), info.Name))
-				if serr != nil || fi.Size() != *info.Length || !fi.ModTime().Equal(*info.Completed) {
-					if err := d.db.Update(d.ctx, torrentInfoReset(info.Name, info.Hash, *info.Length)); err != nil {
-						if serr != nil {
+				statError := serr != nil
+				lengthMismatch := info.Length == nil || fi.Size() != *info.Length
+				completedMismatch := info.Completed == nil || !fi.ModTime().Equal(*info.Completed)
+				if statError || lengthMismatch || completedMismatch {
+					infoLen := int64(0)
+					if info.Length != nil {
+						infoLen = *info.Length
+					}
+					if err := d.db.Update(d.ctx, torrentInfoReset(info.Name, info.Hash, infoLen)); err != nil {
+						if statError {
 							log.Error("[snapshots] Failed to reset db entry after stat error", "file", info.Name, "err", err, "stat-err", serr)
 						} else {
 							log.Error("[snapshots] Failed to reset db entry after stat mismatch", "file", info.Name, "err", err)
```
