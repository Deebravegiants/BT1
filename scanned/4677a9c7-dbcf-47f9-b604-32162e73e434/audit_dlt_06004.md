# [?] ethstats: prevent panic if head block is not available (#29020)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-02-19
Source: https://github.com/etclabscore/core-geth/commit/034bc4669ffe92b95155c8331334f47fa8bb4333
Type: security-commit

## Details
ethstats: prevent panic if head block is not available (#29020)

This pull request fixes a flaw in ethstats which can lead to node crash

A panic could happens when the local blockchain is reorging which causes the original head block not to be  reachable (since number->hash canonical mapping is deleted). In order to prevent the panic, the block nilness is now checked in ethstats.

## Patch
### ethstats/ethstats.go
```diff
@@ -611,6 +611,10 @@ func (s *Service) reportBlock(conn *connWrapper, block *types.Block) error {
 	// Gather the block details from the header or block chain
 	details := s.assembleBlockStats(block)
 
+	// Short circuit if the block detail is not available.
+	if details == nil {
+		return nil
+	}
 	// Assemble the block report and send it to the server
 	log.Trace("Sending new block to ethstats", "number", details.Number, "hash", details.Hash)
 
@@ -638,10 +642,16 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 	// check if backend is a full node
 	fullBackend, ok := s.backend.(fullNodeBackend)
 	if ok {
+		// Retrieve current chain head if no block is given.
 		if block == nil {
 			head := fullBackend.CurrentBlock()
 			block, _ = fullBackend.BlockByNumber(context.Background(), rpc.BlockNumber(head.Number.Uint64()))
 		}
+		// Short circuit if no block is available. It might happen when
+		// the blockchain is reorging.
+		if block == nil {
+			return nil
+		}
 		header = block.Header()
 		td = fullBackend.GetTd(context.Background(), header.Hash())
 
```
