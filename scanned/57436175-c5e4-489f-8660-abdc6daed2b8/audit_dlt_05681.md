# [?] Fix data race in downloader

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-22
Source: https://github.com/celo-org/celo-blockchain/commit/bebc4f01759e5315d45bcebd9a7d935d216da12f
Type: security-commit

## Details
Fix data race in downloader

The eth.chainSyncer main loop periodically calls
eth.chainSyncer.startSync which fires off a sync operation in its own
goroutine which will eventually result in Downloader.Cancel being
called.

The eth.chainSyncer also calls Downloader.Cancel when exiting its main
loop.

This resulted in a data race on Downloader.ancientLimit, the solution
was to add a mutex to lock over Downloader.ancientLimit in
Downloader.Cancel.

==================
WARNING: DATA RACE
Write at 0x00c01a0e3ce0 by goroutine 466:
  github.com/celo-org/celo-blockchain/eth/downloader.(*Downloader).Cancel()
      /home/pierspowlesland/projects/celo-blockchain/eth/downloader/downloader.go:615 +0x68
  github.com/celo-org/celo-blockchain/eth/downloader.(*Downloader).synchronise()
      /home/pierspowlesland/projects/celo-blockchain/eth/downloader/downloader.go:444 +0x601
  github.com/celo-org/celo-blockchain/eth/downloader.(*Downloader).Synchronise()
      /home/pierspowlesland/projects/celo-blockchain/eth/downloader/downloader.go:354 +0xb5
  github.com/celo-org/celo-blockchain/eth.(*ProtocolManager).doSync()
      /home/pierspowlesland/projects/celo-blockchain/eth/sync.go:327 +0x1ad
  github.com/celo-org/celo-blockchain/eth.(*chainSyncer).startSync.func1()
      /home/pierspowlesland/projects/celo-blockchain/eth/sync.go:303 +0x59

Previous write at 0x00c01a0e3ce0 by goroutine 182:
  github.com/celo-org/celo-blockchain/eth/downloader.(*Downloader).Cancel()
      /home/pierspowlesland/projects/celo-blockchain/eth/downloader/downloader.go:615 +0x68
  github.com/celo-org/celo-blockchain/eth/downloader.(*Downloader).Terminate()
      /home/pierspowlesland/projects/celo-blockchain/eth/downloader/downloader.go:635 +0xcc
  github.com/celo-org/celo-blockchain/eth.(*chainSyncer).loop()
      /home/pierspowlesland/projects/celo-blockchain/eth/sync.go:232 +0x65b

## Patch
### eth/downloader/downloader.go
```diff
@@ -121,6 +121,7 @@ type Downloader struct {
 	notified        int32
 	committed       int32
 	ancientLimit    uint64 // The maximum block number which can be regarded as ancient data.
+	ancientLimitMu  sync.Mutex
 
 	// Channels
 	headerCh      chan dataPack        // Channel receiving inbound block headers
@@ -646,6 +647,10 @@ func (d *Downloader) cancel() {
 func (d *Downloader) Cancel() {
 	d.cancel()
 	d.cancelWg.Wait()
+	d.ancientLimitMu.Lock()
+	defer d.ancientLimitMu.Unlock()
+	d.ancientLimit = 0
+	log.Debug("Reset ancient limit to zero")
 }
 
 // Terminate interrupts the downloader, canceling all pending operations.
```
