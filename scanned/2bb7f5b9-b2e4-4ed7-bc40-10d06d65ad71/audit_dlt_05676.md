# [?] fix(rpc): eth_simulateV1 method handler crash (#1955)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-01-20
Source: https://github.com/0xPolygon/bor/commit/ec7192a693f25c13b5f71f5ef0af71cfb357e800
Type: security-commit

## Details
fix(rpc): eth_simulateV1 method handler crash (#1955)

* Verify BlobScheduleConfig before calling CalcBlobFee

* set Nil withdrawals for bor simulation

* simChainHeadReader implements core.BorStateSyncer

* simplify fork checking

* lint fixing

* Add non nil chainConfig for testcase

---------

Co-authored-by: Pratik Patil <pratikspatil024@gmail.com>

## Patch
### core/blockchain.go
```diff
@@ -3688,7 +3688,7 @@ func (bc *BlockChain) recoverAncestors(block *types.Block, makeWitness bool) (co
 // processing of a block. These logs are later announced as deleted or reborn.
 func (bc *BlockChain) collectLogs(b *types.Block, removed bool) []*types.Log {
 	var blobGasPrice *big.Int
-	if b.ExcessBlobGas() != nil {
+	if b.ExcessBlobGas() != nil && bc.chainConfig.BlobScheduleConfig != nil {
 		blobGasPrice = eip4844.CalcBlobFee(bc.chainConfig, b.Header())
 	}
 	receipts := rawdb.ReadRawReceipts(bc.db, b.Hash(), b.NumberU64())
```

### core/blockchain_reader.go
```diff
@@ -293,7 +293,7 @@ func (bc *BlockChain) GetCanonicalReceipt(tx *types.Transaction, blockHash commo
 		return nil, fmt.Errorf("block header is not found, %d, %x", blockNumber, blockHash)
 	}
 	var blobGasPrice *big.Int
-	if header.ExcessBlobGas != nil {
+	if header.ExcessBlobGas != nil && bc.chainConfig.BlobScheduleConfig != nil {
 		blobGasPrice = eip4844.CalcBlobFee(bc.chainConfig, header)
 	}
 	receipt, ctx, err := rawdb.ReadCanonicalRawReceipt(bc.db, blockHash, blockNumber, txIndex)
```

### core/chain_makers.go
```diff
@@ -464,7 +464,7 @@ func GenerateChain(config *params.ChainConfig, parent *types.Block, engine conse
 			txs = txs[:len(receipts)]
 		}
 		var blobGasPrice *big.Int
-		if block.ExcessBlobGas() != nil {
+		if block.ExcessBlobGas() != nil && cm.config.BlobScheduleConfig != nil {
 			blobGasPrice = eip4844.CalcBlobFee(cm.config, block.Header())
 		}
 		if err := receipts.DeriveFields(config, block.Hash(), block.NumberU64(), block.Time(), block.BaseFee(), blobGasPrice, txs); err != nil {
@@ -577,7 +577,7 @@ func GenerateVerkleChain(config *params.ChainConfig, parent *types.Block, engine
 			txs = txs[:len(receipts)]
 		}
 		var blobGasPrice *big.Int
-		if block.ExcessBlobGas() != nil {
+		if block.ExcessBlobGas() != nil && cm.config.BlobScheduleConfig != nil {
 			blobGasPrice = eip4844.CalcBlobFee(cm.config, block.Header())
 		}
 		if err := receipts.DeriveFields(config, block.Hash(), block.NumberU64(), block.Time(), block.BaseFee(), blobGasPrice, txs); err != nil {
```

### core/evm.go
```diff
@@ -71,8 +71,12 @@ func NewEVMBlockContext(header *types.Header, chain ChainContext, author *common
 	if header.BaseFee != nil {
 		baseFee = new(big.Int).Set(header.BaseFee)
 	}
-	if header.ExcessBlobGas != nil {
-		blobBaseFee = eip4844.CalcBlobFee(chain.Config(), header)
+	// Only calculate blob fee if the fork actually supports blob transactions (Cancun or later)
+	// and the chain has a BlobScheduleConfig configured
+	if header.ExcessBlobGas != nil && chain.Config().BlobScheduleConfig != nil {
+		if chain.Config().IsCancun(header.Number) {
+			blobBaseFee = eip4844.CalcBlobFee(chain.Config(), header)
+		}
 	}
 	if header.Difficulty.Sign() == 0 {
 		random = &header.MixDigest
```

### core/txpool/blobpool/blobpool.go
```diff
@@ -424,7 +424,7 @@ func (p *BlobPool) Init(gasTip uint64, head *types.Header, reserver txpool.Reser
 		basefee = uint256.MustFromBig(eip1559.CalcBaseFee(p.chain.Config(), p.head))
 		blobfee = uint256.NewInt(params.BlobTxMinBlobGasprice)
 	)
-	if p.head.ExcessBlobGas != nil {
+	if p.head.ExcessBlobGas != nil && p.chain.Config().BlobScheduleConfig != nil {
 		blobfee = uint256.MustFromBig(eip4844.CalcBlobFee(p.chain.Config(), p.head))
 	}
 	p.evict = newPriceHeap(basefee, blobfee, p.index)
```

### eth/api_backend.go
```diff
@@ -511,7 +511,7 @@ func (b *EthAPIBackend) FeeHistory(ctx context.Context, blockCount uint64, lastB
 }
 
 func (b *EthAPIBackend) BlobBaseFee(ctx context.Context) *big.Int {
-	if excess := b.CurrentHeader().ExcessBlobGas; excess != nil {
+	if excess := b.CurrentHeader().ExcessBlobGas; excess != nil && b.ChainConfig().BlobScheduleConfig != nil {
 		return eip4844.CalcBlobFee(b.ChainConfig(), b.CurrentHeader())
 	}
 	return nil
```

### eth/tracers/live/supply.go
```diff
@@ -166,7 +166,7 @@ func (s *supplyTracer) onBlockStart(ev tracing.BlockEvent) {
 		s.delta.Burn.EIP1559 = burn
 	}
 	// Blob burnt gas
-	if blobGas := ev.Block.BlobGasUsed(); blobGas != nil && *blobGas > 0 && ev.Block.ExcessBlobGas() != nil {
+	if blobGas := ev.Block.BlobGasUsed(); blobGas != nil && *blobGas > 0 && ev.Block.ExcessBlobGas() != nil && s.chainConfig.BlobScheduleConfig != nil {
 		var (
 			baseFee = eip4844.CalcBlobFee(s.chainConfig, ev.Block.Header())
 			burn    = new(big.Int).Mul(new(big.Int).SetUint64(*blobGas), baseFee)
```

### internal/ethapi/simulate.go
```diff
@@ -33,6 +33,7 @@ import (
 	"github.com/ethereum/go-ethereum/core/state"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/core/vm"
+	"github.com/ethereum/go-ethereum/event"
 	"github.com/ethereum/go-ethereum/internal/ethapi/override"
 	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/rpc"
@@ -137,6 +138,21 @@ func (m *simChainHeadReader) GetHeader(hash common.Hash, number uint64) *types.H
 	return header
 }
 
+// SetStateSync implements core.BorStateSyncer for Bor consensus compatibility.
+// Since this is a simulation, we don't need to actually store state sync data.
+func (m *simChainHeadReader) SetStateSync(stateData []*types.StateSyncData) {
+	// No-op for simulation
+}
+
+// SubscribeStateSyncEvent implements core.BorStateSyncer for Bor consensus compatibility.
+// Returns a no-op subscription since we don't need state sync events in simulation.
+func (m *simChainHeadReader) SubscribeStateSyncEvent(ch chan<- core.StateSyncEvent) event.Subscription {
+	return event.NewSubscription(func(quit <-chan struct{}) error {
+		<-quit
+		return nil
+	})
+}
+
 func (m *simChainHeadReader) GetHeaderByNumber(number uint64) *types.Header {
 	header, err := m.Backend.HeaderByNumber(m.Context, rpc.BlockNumber(number))
 	if err != nil {
@@ -352,7 +368,12 @@ func (sim *simulator) processBlock(ctx context.Context, block *simBlock, header,
 		reqHash := types.CalcRequestsHash(requests)
 		header.RequestsHash = &reqHash
 	}
-	blockBody := &types.Body{Transactions: txes, Withdrawals: *block.BlockOverrides.Withdrawals}
+	// For Bor chains, Withdrawals will be nil, so we need to handle that
+	var withdrawals types.Withdrawals
+	if block.BlockOverrides.Withdrawals != nil {
+		withdrawals = *block.BlockOverrides.Withdrawals
+	}
+	blockBody := &types.Body{Transactions: txes, Withdrawals: withdrawals}
 	chainHeadReader := &simChainHeadReader{ctx, sim.b}
 	b, receipts, err := sim.b.Engine().FinalizeAndAssemble(chainHeadReader, header, sim.state, blockBody, receipts)
 	_ = receipts // mark unused
@@ -420,7 +441,9 @@ func (sim *simulator) sanitizeChain(blocks []simBlock) ([]simBlock, error) {
 			n := new(big.Int).Add(prevNumber, big.NewInt(1))
 			block.BlockOverrides.Number = (*hexutil.Big)(n)
 		}
-		if block.BlockOverrides.Withdrawals == nil {
+		// Only set withdrawals for non-Bor chains (Ethereum mainnet and testnets)
+		// Bor/Polygon doesn't support withdrawals even post-Shanghai
+		if block.BlockOverrides.Withdrawals == nil && sim.chainConfig.Bor == nil {
 			block.BlockOverrides.Withdrawals = &types.Withdrawals{}
 		}
 		diff := new(big.Int).Sub(block.BlockOverrides.Number.ToInt(), prevNumber)
@@ -437,12 +460,16 @@ func (sim *simulator) sanitizeChain(blocks []simBlock) ([]simBlock, error) {
 			for i := uint64(0); i < gap.Uint64(); i++ {
 				n := new(big.Int).Add(prevNumber, big.NewInt(int64(i+1)))
 				t := prevTimestamp + timestampIncrement
+				overrides := &override.BlockOverrides{
+					Number: (*hexutil.Big)(n),
+					Time:   (*hexutil.Uint64)(&t),
+				}
+				// Only set withdrawals for non-Bor chains
+				if sim.chainConfig.Bor == nil {
+					overrides.Withdrawals = &types.Withdrawals{}
+				}
 				b := simBlock{
-					BlockOverrides: &override.BlockOverrides{
-						Number:      (*hexutil.Big)(n),
-						Time:        (*hexutil.Uint64)(&t),
-						Withdrawals: &types.Withdrawals{},
-					},
+					BlockOverrides: overrides,
 				}
 				prevTimestamp = t
 				res = append(res, b)
@@ -482,7 +509,8 @@ func (sim *simulator) makeHeaders(blocks []simBlock) ([]*types.Header, error) {
 		overrides := block.BlockOverrides
 
 		var withdrawalsHash *common.Hash
-		if sim.chainConfig.IsShanghai(overrides.Number.ToInt()) {
+		// Only set withdrawals hash for non-Bor chains that have Shanghai fork
+		if sim.chainConfig.IsShanghai(overrides.Number.ToInt()) && sim.chainConfig.Bor == nil {
 			withdrawalsHash = &types.EmptyWithdrawalsHash
 		}
 		var parentBeaconRoot *common.Hash
```

### internal/ethapi/simulate_test.go
```diff
@@ -23,6 +23,7 @@ import (
 	"github.com/ethereum/go-ethereum/common/hexutil"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/internal/ethapi/override"
+	"github.com/ethereum/go-ethereum/params"
 )
 
 func TestSimulateSanitizeBlockOrder(t *testing.T) {
@@ -80,7 +81,10 @@ func TestSimulateSanitizeBlockOrder(t *testing.T) {
 			err:           "block timestamps must be in order: 72 <= 72",
 		},
 	} {
-		sim := &simulator{base: &types.Header{Number: big.NewInt(int64(tc.baseNumber)), Time: tc.baseTimestamp}}
+		sim := &simulator{
+			base:        &types.Header{Number: big.NewInt(int64(tc.baseNumber)), Time: tc.baseTimestamp},
+			chainConfig: params.TestChainConfig, // In real usage, sanitizeChain is always called with chainConfig
+		}
 		res, err := sim.sanitizeChain(tc.blocks)
 		if err != nil {
 			if err.Error() == tc.err {
```

### internal/ethapi/transaction_args.go
```diff
@@ -255,7 +255,7 @@ func (args *TransactionArgs) setFeeDefaults(ctx context.Context, b Backend, head
 // setCancunFeeDefaults fills in reasonable default fee values for unspecified fields.
 func (args *TransactionArgs) setCancunFeeDefaults(config *params.ChainConfig, head *types.Header) {
 	// Set maxFeePerBlobGas if it is missing.
-	if args.BlobHashes != nil && args.BlobFeeCap == nil {
+	if args.BlobHashes != nil && args.BlobFeeCap == nil && config.BlobScheduleConfig != nil {
 		blobBaseFee := eip4844.CalcBlobFee(config, head)
 		// Set the max fee to be 2 times larger than the previous block's blob base fee.
 		// The additional slack allows the tx to not become invalidated if the base
```
