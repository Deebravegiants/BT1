# [?] added error handeling in ethstats.go which prevents node to panic (#1249)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-05-27
Source: https://github.com/0xPolygon/bor/commit/5f6a76bafe34254896902f70ff2e498e8179ec42
Type: security-commit

## Details
added error handeling in ethstats.go which prevents node to panic (#1249)

## Patch
### ethstats/ethstats.go
```diff
@@ -689,6 +689,11 @@ func (s *Service) reportBlock(conn *connWrapper, block *types.Block) error {
 	// Gather the block details from the header or block chain
 	details := s.assembleBlockStats(block)
 
+	// Short circuit if the block detail is not available.
+	if details == nil {
+		return nil
+	}
+
 	// Assemble the block report and send it to the server
 	log.Trace("Sending new block to ethstats", "number", details.Number, "hash", details.Hash)
 
@@ -712,14 +717,21 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 		td     *big.Int
 		txs    []txStats
 		uncles []*types.Header
+		err    error
 	)
 
 	// check if backend is a full node
 	fullBackend, ok := s.backend.(fullNodeBackend)
 	if ok {
 		if block == nil {
 			head := fullBackend.CurrentBlock()
-			block, _ = fullBackend.BlockByNumber(context.Background(), rpc.BlockNumber(head.Number.Uint64()))
+			block, err = fullBackend.BlockByNumber(context.Background(), rpc.BlockNumber(head.Number.Uint64()))
+			// Short circuit if no block is available. It might happen when
+			// the blockchain is reorging.
+			if err != nil {
+				log.Error("Failed to retrieve block by number", "err", err)
+				return nil
+			}
 		}
 
 		header = block.Header()
@@ -791,8 +803,12 @@ func (s *Service) reportHistory(conn *connWrapper, list []uint64) error {
 		fullBackend, ok := s.backend.(fullNodeBackend)
 		// Retrieve the next block if it's known to us
 		var block *types.Block
+		var err error
 		if ok {
-			block, _ = fullBackend.BlockByNumber(context.Background(), rpc.BlockNumber(number)) // TODO ignore error here ?
+			block, err = fullBackend.BlockByNumber(context.Background(), rpc.BlockNumber(number))
+			if err != nil {
+				log.Error("Failed to retrieve block by number", "err", err)
+			}
 		} else {
 			if header, _ := s.backend.HeaderByNumber(context.Background(), rpc.BlockNumber(number)); header != nil {
 				block = types.NewBlockWithHeader(header)
```
