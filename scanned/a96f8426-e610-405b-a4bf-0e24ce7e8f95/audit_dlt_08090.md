# [?] Add missing return; avoids panic.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2013-10-28
Source: https://github.com/btcsuite/btcd/commit/3c405563bdcfc7ec8e48733ac1dd8b23015ee9c6
Type: security-commit

## Details
Add missing return; avoids panic.

## Patch
### rpcserver.go
```diff
@@ -489,6 +489,7 @@ func jsonRead(body []byte, s *rpcServer, walletNotification chan []byte) (reply
 		if err != nil {
 			log.Errorf("RPCS: Error fetching sha: %v", err)
 			err = btcjson.ErrBlockNotFound
+			return
 		}
 		idx := blk.Height()
 		var buf []byte
```
