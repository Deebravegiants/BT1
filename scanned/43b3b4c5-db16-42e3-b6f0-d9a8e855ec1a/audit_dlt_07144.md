# [?] downloader: fix edgecase where returned index is OOB for downloader (#18335)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-12-20
Source: https://github.com/celo-org/celo-blockchain/commit/5f251a6448b3385015ab531c35071743f93cafae
Type: security-commit

## Details
downloader: fix edgecase where returned index is OOB for downloader (#18335)

* downloader: fix edgecase where returned index is OOB for downloader

* downloader: documentation

Co-Authored-By: holiman <martin@swende.se>

## Patch
### eth/downloader/downloader.go
```diff
@@ -1488,7 +1488,15 @@ func (d *Downloader) importBlockResults(results []*fetchResult) error {
 		blocks[i] = types.NewBlockWithHeader(result.Header).WithBody(result.Transactions, result.Uncles)
 	}
 	if index, err := d.blockchain.InsertChain(blocks); err != nil {
-		log.Debug("Downloaded item processing failed", "number", results[index].Header.Number, "hash", results[index].Header.Hash(), "err", err)
+		if index < len(results) {
+			log.Debug("Downloaded item processing failed", "number", results[index].Header.Number, "hash", results[index].Header.Hash(), "err", err)
+		} else {
+			// The InsertChain method in blockchain.go will sometimes return an out-of-bounds index,
+			// when it needs to preprocess blocks to import a sidechain.
+			// The importer will put together a new list of blocks to import, which is a superset
+			// of the blocks delivered from the downloader, and the indexing will be off.
+			log.Debug("Downloaded item processing failed on sidechain import", "index", index, "err", err)
+		}
 		return errInvalidChain
 	}
 	return nil
```
