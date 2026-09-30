# [?] Fix panics on non-existing block RPC requests

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-02-21
Source: https://github.com/0xsoniclabs/sonic/commit/558fe990823c1a8f6f0c8f7d4acc42adf4947eb2
Type: security-commit

## Details
Fix panics on non-existing block RPC requests

## Patch
### ethapi/api.go
```diff
@@ -998,7 +998,7 @@ func DoEstimateGas(ctx context.Context, b Backend, args TransactionArgs, blockNr
 	// Recap the highest gas limit with account's available balance.
 	if feeCap.BitLen() != 0 {
 		state, _, err := b.StateAndHeaderByNumberOrHash(ctx, blockNrOrHash)
-		if err != nil {
+		if state == nil || err != nil {
 			return 0, err
 		}
 		balance := state.GetBalance(*args.From) // from can't be nil
@@ -1547,7 +1547,7 @@ func (s *PublicTransactionPoolAPI) GetTransactionByHash(ctx context.Context, has
 	}
 	if tx != nil {
 		header, err := s.b.HeaderByNumber(ctx, rpc.BlockNumber(blockNumber))
-		if err != nil {
+		if header == nil || err != nil {
 			return nil, err
 		}
 		return newRPCTransaction(tx, header.Hash, blockNumber, index, header.BaseFee), nil
@@ -1947,14 +1947,14 @@ func (api *PublicDebugAPI) SeedHash(ctx context.Context, number uint64) (string,
 func (api *PublicDebugAPI) BlocksTransactionTimes(ctx context.Context, untilBlock rpc.BlockNumber, maxBlocks hexutil.Uint64) (map[hexutil.Uint64]hexutil.Uint, error) {
 
 	until, err := api.b.HeaderByNumber(ctx, untilBlock)
-	if err != nil {
+	if until == nil || err != nil {
 		return nil, err
 	}
 	untilN := until.Number.Uint64()
 	times := map[hexutil.Uint64]hexutil.Uint{}
 	for i := untilN; i >= 1 && i+uint64(maxBlocks) > untilN; i-- {
 		b, err := api.b.BlockByNumber(ctx, rpc.BlockNumber(i))
-		if err != nil {
+		if b == nil || err != nil {
 			return nil, err
 		}
 		if b.Transactions.Len() == 0 {
```

### gossip/ethapi_backend.go
```diff
@@ -51,6 +51,7 @@ func (b *EthAPIBackend) CurrentBlock() *evmcore.EvmBlock {
 	return b.state.CurrentBlock()
 }
 
+// HeaderByNumber returns evm block header by its number, or nil if not exists.
 func (b *EthAPIBackend) HeaderByNumber(ctx context.Context, number rpc.BlockNumber) (*evmcore.EvmHeader, error) {
 	blk, err := b.BlockByNumber(ctx, number)
 	if err != nil {
@@ -62,7 +63,7 @@ func (b *EthAPIBackend) HeaderByNumber(ctx context.Context, number rpc.BlockNumb
 	return blk.Header(), err
 }
 
-// HeaderByHash returns evm header by its (atropos) hash.
+// HeaderByHash returns evm block header by its (atropos) hash, or nil if not exists.
 func (b *EthAPIBackend) HeaderByHash(ctx context.Context, h common.Hash) (*evmcore.EvmHeader, error) {
 	index := b.svc.store.GetBlockIndex(hash.Event(h))
 	if index == nil {
@@ -71,7 +72,7 @@ func (b *EthAPIBackend) HeaderByHash(ctx context.Context, h common.Hash) (*evmco
 	return b.HeaderByNumber(ctx, rpc.BlockNumber(*index))
 }
 
-// BlockByNumber returns block by its number.
+// BlockByNumber returns evm block by its number, or nil if not exists.
 func (b *EthAPIBackend) BlockByNumber(ctx context.Context, number rpc.BlockNumber) (*evmcore.EvmBlock, error) {
 	if number == rpc.PendingBlockNumber {
 		number = rpc.LatestBlockNumber
@@ -88,6 +89,7 @@ func (b *EthAPIBackend) BlockByNumber(ctx context.Context, number rpc.BlockNumbe
 	return blk, nil
 }
 
+// StateAndHeaderByNumberOrHash returns evm state and block header by block number or block hash, err if not exists.
 func (b *EthAPIBackend) StateAndHeaderByNumberOrHash(ctx context.Context, blockNrOrHash rpc.BlockNumberOrHash) (*state.StateDB, *evmcore.EvmHeader, error) {
 	var header *evmcore.EvmHeader
 	if number, ok := blockNrOrHash.Number(); ok && (number == rpc.LatestBlockNumber || number == rpc.PendingBlockNumber) {
```
