# [?] eth/downloader: fix data race around the ancientlimit (#21681)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-10-09
Source: https://github.com/ethereum/go-ethereum/commit/905ed109edfda340ccd3641ebad4e0ff5dc73440
Type: security-commit

## Details
eth/downloader: fix data race around the ancientlimit (#21681)

* eth/downloader: fix data race around the ancientlimit

* eth/downloader: initialize the ancientlimit as 0

## Patch
### eth/downloader/downloader.go
```diff
@@ -515,6 +515,8 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 			d.ancientLimit = d.checkpoint
 		} else if height > fullMaxForkAncestry+1 {
 			d.ancientLimit = height - fullMaxForkAncestry - 1
+		} else {
+			d.ancientLimit = 0
 		}
 		frozen, _ := d.stateDB.Ancients() // Ignore the error here since light client can also hit here.
 
@@ -606,9 +608,6 @@ func (d *Downloader) cancel() {
 func (d *Downloader) Cancel() {
 	d.cancel()
 	d.cancelWg.Wait()
-
-	d.ancientLimit = 0
-	log.Debug("Reset ancient limit to zero")
 }
 
 // Terminate interrupts the downloader, canceling all pending operations.
```
