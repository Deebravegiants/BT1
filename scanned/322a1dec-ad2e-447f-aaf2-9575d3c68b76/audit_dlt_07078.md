# [?] Fix panic in debug muxxing and restore GOPPROF handler route (#16032)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-07-10
Source: https://github.com/erigontech/erigon/commit/0586947cc71484445996d4658d7895ddbeedbeac
Type: security-commit

## Details
Fix panic in debug muxxing and restore GOPPROF handler route (#16032)

Panic introduced by https://github.com/erigontech/erigon/pull/15982, and
route restored per
https://github.com/erigontech/erigon/pull/15982#issuecomment-3048460301.

## Patch
### cmd/downloader/main.go
```diff
@@ -22,7 +22,6 @@ import (
 	"fmt"
 	"io/fs"
 	"net"
-	"net/http"
 	"net/url"
 	"os"
 	"path/filepath"
@@ -303,7 +302,7 @@ func Downloader(ctx context.Context, logger log.Logger) error {
 	defer d.Close()
 	logger.Info("[snapshots] Start bittorrent server", "my_peer_id", fmt.Sprintf("%x", d.TorrentClient().PeerID()))
 
-	d.HandleTorrentClientStatus(http.DefaultServeMux)
+	d.HandleTorrentClientStatus(nil)
 
 	err = d.AddTorrentsFromDisk(ctx)
 	if err != nil {
```

### erigon-db/downloader/downloader.go
```diff
@@ -1344,12 +1344,17 @@ func (d *Downloader) Completed() bool {
 	return d.allTorrentsComplete()
 }
 
-// Expose torrent client status to HTTP on the public/default serve mux used by GOPPROF=http. Only
-// do this if you have a single instance.
+// Expose torrent client status to HTTP on the public/default serve mux used by GOPPROF=http, and
+// the provided "debug" mux if non-nil. Only do this if you have a single instance of a Downloader.
 func (d *Downloader) HandleTorrentClientStatus(debugMux *http.ServeMux) {
-	debugMux.HandleFunc("/downloader/torrents", func(w http.ResponseWriter, r *http.Request) {
+	h := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
 		d.torrentClient.WriteStatus(w)
 	})
+	p := "/downloader/torrentClientStatus"
+	http.Handle(p, h)
+	if debugMux != nil {
+		debugMux.Handle(p, h)
+	}
 }
 
 func (d *Downloader) spawn(f func()) {
```
