# [?] Fixed panic on new mined block event when block download is disabled (#13849)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-02-18
Source: https://github.com/erigontech/erigon/commit/e941501cad3052ef798b92c3568c22d7393ab616
Type: security-commit

## Details
Fixed panic on new mined block event when block download is disabled (#13849)

## Patch
### eth/backend.go
```diff
@@ -889,14 +889,16 @@ func New(ctx context.Context, stack *node.Node, config *ethconfig.Config, logger
 		for {
 			select {
 			case b := <-backend.minedBlocks:
-				// Add mined header and block body before broadcast. This is because the broadcast call
-				// will trigger the staged sync which will require headers and blocks to be available
-				// in their respective cache in the download stage. If not found, it would cause a
-				// liveness issue for the chain.
-				if err := backend.sentriesClient.Hd.AddMinedHeader(b.Header()); err != nil {
-					logger.Error("add mined block to header downloader", "err", err)
+				if !sentryMcDisableBlockDownload {
+					// Add mined header and block body before broadcast. This is because the broadcast call
+					// will trigger the staged sync which will require headers and blocks to be available
+					// in their respective cache in the download stage. If not found, it would cause a
+					// liveness issue for the chain.
+					if err := backend.sentriesClient.Hd.AddMinedHeader(b.Header()); err != nil {
+						logger.Error("add mined block to header downloader", "err", err)
+					}
+					backend.sentriesClient.Bd.AddToPrefetch(b.Header(), b.RawBody())
 				}
-				backend.sentriesClient.Bd.AddToPrefetch(b.Header(), b.RawBody())
 
 				//p2p
 				//backend.sentriesClient.BroadcastNewBlock(context.Background(), b, b.Difficulty())
```
