# [?] eth/downloader: fix test panic (#35215)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-06-25
Source: https://github.com/ethereum/go-ethereum/commit/a63e2f124716c1f86e0a841d0abad017af21fa05
Type: security-commit

## Details
eth/downloader: fix test panic (#35215)

This PR addresses the panic in tests. As the eventLoop is spun up when
the downloader was closed, the sub will be nil and make the panic
happens.

```
  goroutine 421 [running]:
  github.com/ethereum/go-ethereum/eth/downloader.(*DownloaderAPI).eventLoop(0xcb0e4d0)
      /opt/actions-runner/_work/go-ethereum/go-ethereum/eth/downloader/api.go:91 +0x127
  created by github.com/ethereum/go-ethereum/eth/downloader.NewDownloaderAPI in goroutine 352
      /opt/actions-runner/_work/go-ethereum/go-ethereum/eth/downloader/api.go:50 +0xf2
```

## Patch
### eth/downloader/api.go
```diff
@@ -62,9 +62,12 @@ func NewDownloaderAPI(d *Downloader, chain *core.BlockChain) *DownloaderAPI {
 // If the node is already synced up, then only a single event subscribers will
 // receive is {false}.
 func (api *DownloaderAPI) eventLoop() {
+	events := make(chan SyncEvent, 16)
+	sub := api.d.SubscribeSyncEvents(events)
+	if sub == nil {
+		return
+	}
 	var (
-		events            = make(chan SyncEvent, 16)
-		sub               = api.d.SubscribeSyncEvents(events)
 		syncSubscriptions = make(map[chan interface{}]struct{})
 		checkInterval     = time.Second * 60
 		checkTimer        = time.NewTimer(checkInterval)
```
