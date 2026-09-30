# [?] op-node: Fix uint64 overflow in yParity calculation and use Uint64Strict instead of UInt64 for safety (#18921)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-01-26
Source: https://github.com/ethereum-optimism/optimism/commit/b8a91297ea47b224a071db3ae6a721445e9fc8d1
Type: security-commit

## Details
op-node: Fix uint64 overflow in yParity calculation and use Uint64Strict instead of UInt64 for safety (#18921)

* op-node: Use Uint64Strict.

* op-node: Use big.Int to calculate yParity/v to support large chain IDs.

* Update tests to compare big.Int logically

## Patch
### op-node/cmd/batch_decoder/fetch/fetch.go
```diff
@@ -12,6 +12,7 @@ import (
 	"time"
 
 	"github.com/ethereum-optimism/optimism/op-node/rollup/derive"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	"github.com/ethereum-optimism/optimism/op-service/eth"
 	"github.com/ethereum-optimism/optimism/op-service/sources"
 	"github.com/ethereum/go-ethereum/common"
@@ -124,7 +125,7 @@ func fetchBatchesPerBlock(ctx context.Context, client *ethclient.Client, beacon
 				}
 				blobs, err := beacon.GetBlobs(ctx, eth.L1BlockRef{
 					Hash:       block.Hash(),
-					Number:     block.Number().Uint64(),
+					Number:     block.NumberU64(),
 					ParentHash: block.ParentHash(),
 					Time:       block.Time(),
 				}, hashes)
@@ -171,7 +172,7 @@ func fetchBatchesPerBlock(ctx context.Context, client *ethclient.Client, beacon
 				BlockNumber: block.NumberU64(),
 				BlockHash:   block.Hash(),
 				BlockTime:   block.Time(),
-				ChainId:     config.ChainID.Uint64(),
+				ChainId:     bigs.Uint64Strict(config.ChainID),
 				InboxAddr:   config.BatchInbox,
 				Frames:      frames,
 				FrameErrs:   frameErrors,
```

### op-node/cmd/batch_decoder/main.go
```diff
@@ -13,6 +13,7 @@ import (
 	"github.com/ethereum-optimism/optimism/op-node/cmd/batch_decoder/reassemble"
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
 	"github.com/ethereum-optimism/optimism/op-node/rollup/derive"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	"github.com/ethereum-optimism/optimism/op-service/client"
 	"github.com/ethereum-optimism/optimism/op-service/sources"
 	"github.com/ethereum/go-ethereum/common"
@@ -162,7 +163,7 @@ func main() {
 				var rollupCfg *rollup.Config
 				if cliCtx.IsSet("l2-chain-id") {
 					l2ChainID := new(big.Int).SetUint64(cliCtx.Uint64("l2-chain-id"))
-					cfg, err := rollup.LoadOPStackRollupConfig(l2ChainID.Uint64())
+					cfg, err := rollup.LoadOPStackRollupConfig(bigs.Uint64Strict(l2ChainID))
 					if err != nil {
 						return err
 					}
```

### op-node/cmd/genesis/cmd.go
```diff
@@ -198,7 +198,7 @@ var Subcommands = cli.Commands{
 			}
 
 			l2GenesisBlock := l2Genesis.ToBlock()
-			rollupConfig, err := config.RollupConfig(eth.BlockRefFromHeader(l1StartBlock.Header()), l2GenesisBlock.Hash(), l2GenesisBlock.Number().Uint64())
+			rollupConfig, err := config.RollupConfig(eth.BlockRefFromHeader(l1StartBlock.Header()), l2GenesisBlock.Hash(), l2GenesisBlock.NumberU64())
 			if err != nil {
 				return err
 			}
```

### op-node/node/server_test.go
```diff
@@ -17,6 +17,7 @@ import (
 
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
 	"github.com/ethereum-optimism/optimism/op-node/version"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	rpcclient "github.com/ethereum-optimism/optimism/op-service/client"
 	"github.com/ethereum-optimism/optimism/op-service/eth"
 	opmetrics "github.com/ethereum-optimism/optimism/op-service/metrics"
@@ -87,7 +88,7 @@ func TestOutputAtBlock(t *testing.T) {
 	l2Client := &testutils.MockL2Client{}
 	ref := eth.L2BlockRef{
 		Hash:           header.Hash(),
-		Number:         header.Number.Uint64(),
+		Number:         bigs.Uint64Strict(header.Number),
 		ParentHash:     header.ParentHash,
 		Time:           header.Time,
 		L1Origin:       eth.BlockID{},
```

### op-node/p2p/discovery.go
```diff
@@ -29,6 +29,7 @@ import (
 
 	"github.com/ethereum-optimism/optimism/op-node/p2p/store"
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 )
 
 // force to use the new chainhash module, and not the legacy chainhash package btcd module
@@ -77,7 +78,7 @@ func (conf *Config) Discovery(log log.Logger, rollupCfg *rollup.Config, tcpPort
 		return nil, nil, fmt.Errorf("no TCP port to put in discovery record")
 	}
 	dat := OpStackENRData{
-		chainID: rollupCfg.L2ChainID.Uint64(),
+		chainID: bigs.Uint64Strict(rollupCfg.L2ChainID),
 		version: 0,
 	}
 	localNode.Set(&dat)
@@ -221,8 +222,8 @@ func FilterEnodes(log log.Logger, cfg *rollup.Config) func(node *enode.Node) boo
 			return false
 		}
 		// check chain ID matches
-		if cfg.L2ChainID.Uint64() != dat.chainID {
-			log.Trace("discovered node record has no matching chain ID", "node", node.ID(), "got", dat.chainID, "expected", cfg.L2ChainID.Uint64())
+		if bigs.Uint64Strict(cfg.L2ChainID) != dat.chainID {
+			log.Trace("discovered node record has no matching chain ID", "node", node.ID(), "got", dat.chainID, "expected", cfg.L2ChainID)
 			return false
 		}
 		// check version matches
```

### op-node/p2p/prepared.go
```diff
@@ -15,6 +15,7 @@ import (
 	"github.com/ethereum/go-ethereum/p2p/enr"
 
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 )
 
 // Prepared provides a p2p host and discv5 service that is already set up.
@@ -52,7 +53,7 @@ func (p *Prepared) Host(log log.Logger, reporter metrics.Reporter, metrics HostM
 func (p *Prepared) Discovery(log log.Logger, rollupCfg *rollup.Config, tcpPort uint16) (*enode.LocalNode, *discover.UDPv5, error) {
 	if p.LocalNode != nil {
 		dat := OpStackENRData{
-			chainID: rollupCfg.L2ChainID.Uint64(),
+			chainID: bigs.Uint64Strict(rollupCfg.L2ChainID),
 			version: 0,
 		}
 		p.LocalNode.Set(&dat)
```

### op-node/rollup/derive/batch_test.go
```diff
@@ -2,14 +2,17 @@ package derive
 
 import (
 	"bytes"
+	"fmt"
 	"math/big"
 	"math/rand"
+	"reflect"
 	"testing"
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/common/hexutil"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/rlp"
+	"github.com/google/go-cmp/cmp"
 	"github.com/stretchr/testify/require"
 
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
@@ -164,7 +167,7 @@ func TestBatchRoundTrip(t *testing.T) {
 			_, err := DeriveSpanBatch(&dec, blockTime, genesisTimestamp, chainID)
 			require.NoError(t, err)
 		}
-		require.Equal(t, batch, &dec, "Batch not equal test case %v", i)
+		requireEqual(t, batch, &dec, "Batch not equal test case %v", i)
 	}
 }
 
@@ -212,6 +215,34 @@ func TestBatchRoundTripRLP(t *testing.T) {
 			_, err = DeriveSpanBatch(&dec, blockTime, genesisTimestamp, chainID)
 			require.NoError(t, err)
 		}
-		require.Equal(t, batch, &dec, "Batch not equal test case %v", i)
+		requireEqual(t, batch, &dec, "Batch not equal test case %v", i)
+	}
+}
+
+// requireEqual compares two values for equality using cmp.Diff with options
+// that handle *big.Int comparison correctly (using Cmp() for logical equality
+// rather than reflect.DeepEqual which compares internal structure).
+func requireEqual(t *testing.T, expected, actual any, msgAndArgs ...any) {
+	t.Helper()
+	opts := cmp.Options{
+		// Compare *big.Int using Cmp() for logical equality
+		cmp.Comparer(func(a, b *big.Int) bool {
+			if a == nil && b == nil {
+				return true
+			}
+			if a == nil || b == nil {
+				return false
+			}
+			return a.Cmp(b) == 0
+		}),
+		// Allow comparison of unexported fields in all structs
+		cmp.Exporter(func(reflect.Type) bool { return true }),
+	}
+	if diff := cmp.Diff(expected, actual, opts); diff != "" {
+		if len(msgAndArgs) > 0 {
+			t.Errorf("%v:\n%s", fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]), diff)
+		} else {
+			t.Errorf("values not equal:\n%s", diff)
+		}
 	}
 }
```

### op-node/rollup/derive/deposit_log.go
```diff
@@ -11,6 +11,7 @@ import (
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/crypto"
 
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	"github.com/ethereum-optimism/optimism/op-service/eth"
 )
 
@@ -119,7 +120,7 @@ func unmarshalDepositVersion0(dep *types.DepositTx, to common.Address, opaqueDat
 	if !gas.IsUint64() {
 		return fmt.Errorf("bad gas value: %x", opaqueData[offset:offset+8])
 	}
-	dep.Gas = gas.Uint64()
+	dep.Gas = bigs.Uint64Strict(gas)
 	offset += 8
 
 	// uint8 isCreation
```

### op-node/rollup/derive/span_batch_test.go
```diff
@@ -245,7 +245,7 @@ func TestSpanBatchPayload(t *testing.T) {
 	err = sb.txs.recoverV(chainID)
 	require.NoError(t, err)
 
-	require.Equal(t, rawSpanBatch.spanBatchPayload, sb.spanBatchPayload)
+	requireEqual(t, rawSpanBatch.spanBatchPayload, sb.spanBatchPayload)
 }
 
 func TestSpanBatchBlockCount(t *testing.T) {
@@ -310,7 +310,7 @@ func TestSpanBatchTxs(t *testing.T) {
 	err = sb.txs.recoverV(chainID)
 	require.NoError(t, err)
 
-	require.Equal(t, rawSpanBatch.txs, sb.txs)
+	requireEqual(t, rawSpanBatch.txs, sb.txs)
 }
 
 func TestSpanBatchRoundTrip(t *testing.T) {
@@ -330,7 +330,7 @@ func TestSpanBatchRoundTrip(t *testing.T) {
 	err = sb.txs.recoverV(chainID)
 	require.NoError(t, err)
 
-	require.Equal(t, rawSpanBatch, &sb)
+	requireEqual(t, rawSpanBatch, &sb)
 }
 
 func TestSpanBatchDerive(t *testing.T) {
```

### op-node/rollup/derive/span_batch_txs.go
```diff
@@ -8,6 +8,7 @@ import (
 	"io"
 	"math/big"
 
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/common/hexutil"
 	"github.com/ethereum/go-ethereum/core/types"
@@ -34,7 +35,7 @@ type spanBatchTxs struct {
 }
 
 type spanBatchSignature struct {
-	v uint64
+	v *big.Int
 	r *uint256.Int
 	s *uint256.Int
 }
@@ -255,24 +256,24 @@ func (btx *spanBatchTxs) recoverV(chainID *big.Int) error {
 	}
 	protectedBitsIdx := 0
 	for idx, txType := range btx.txTypes {
-		bit := uint64(btx.yParityBits.Bit(idx))
-		var v uint64
+		bit := btx.yParityBits.Bit(idx)
+		var v *big.Int
 		switch txType {
 		case types.LegacyTxType:
 			protectedBit := btx.protectedBits.Bit(protectedBitsIdx)
 			protectedBitsIdx++
 			if protectedBit == 0 {
-				v = 27 + bit
+				// unprotected legacy: v = 27 + yParity
+				v = big.NewInt(int64(27 + bit))
 			} else {
-				// EIP-155
-				v = chainID.Uint64()*2 + 35 + bit
+				// EIP-155: v = chainID * 2 + 35 + yParity
+				v = new(big.Int).Mul(chainID, big.NewInt(2))
+				v.Add(v, big.NewInt(35))
+				v.Add(v, big.NewInt(int64(bit)))
 			}
-		case types.AccessListTxType:
-			v = bit
-		case types.DynamicFeeTxType:
-			v = bit
-		case types.SetCodeTxType:
-			v = bit
+		case types.AccessListTxType, types.DynamicFeeTxType, types.SetCodeTxType:
+			// For non-legacy tx types, v is just the y-parity bit (0 or 1).
+			v = big.NewInt(int64(bit))
 		default:
 			return fmt.Errorf("invalid tx type: %d", txType)
 		}
@@ -356,7 +357,7 @@ func (btx *spanBatchTxs) fullTxs(chainID *big.Int) ([][]byte, error) {
 			to = &btx.txTos[toIdx]
 			toIdx++
 		}
-		v := new(big.Int).SetUint64(btx.txSigs[idx].v)
+		v := btx.txSigs[idx].v
 		r := btx.txSigs[idx].r.ToBig()
 		s := btx.txSigs[idx].s.ToBig()
 		tx, err := stx.convertToFullTx(nonce, gas, to, chainID, v, r, s)
@@ -372,34 +373,36 @@ func (btx *spanBatchTxs) fullTxs(chainID *big.Int) ([][]byte, error) {
 	return txs, nil
 }
 
-func convertVToYParity(v uint64, txType int) (uint, error) {
+func convertVToYParity(v *big.Int, txType int) (uint, error) {
 	var yParityBit uint
 	switch txType {
 	case types.LegacyTxType:
 		if isProtectedV(v, txType) {
 			// EIP-155: v = 2 * chainID + 35 + yParity
 			// v - 35 = yParity (mod 2)
-			yParityBit = uint((v - 35) & 1)
+			vMinus35 := new(big.Int).Sub(v, big.NewInt(35))
+			yParityBit = uint(vMinus35.Bit(0))
 		} else {
 			// unprotected legacy txs must have v = 27 or 28
-			yParityBit = uint(v - 27)
+			yParityBit = uint(bigs.Uint64Strict(v) - 27)
 		}
 	case types.AccessListTxType:
-		yParityBit = uint(v)
+		yParityBit = uint(bigs.Uint64Strict(v))
 	case types.DynamicFeeTxType:
-		yParityBit = uint(v)
+		yParityBit = uint(bigs.Uint64Strict(v))
 	case types.SetCodeTxType:
-		yParityBit = uint(v)
+		yParityBit = uint(bigs.Uint64Strict(v))
 	default:
 		return 0, fmt.Errorf("invalid tx type: %d", txType)
 	}
 	return yParityBit, nil
 }
 
-func isProtectedV(v uint64, txType int) bool {
+func isProtectedV(v *big.Int, txType int) bool {
 	if txType == types.LegacyTxType {
 		// if EIP-155 applied, v = 2 * chainID + 35 + yParity
-		return v != 27 && v != 28
+		// unprotected legacy txs have v = 27 or 28, so protected means v is neither
+		return !bigs.Equal(v, big.NewInt(27)) && !bigs.Equal(v, big.NewInt(28))
 	}
 	// every non legacy tx are protected
 	return true
@@ -447,7 +450,7 @@ func (sbtx *spanBatchTxs) AddTxs(txs [][]byte, chainID *big.Int) error {
 		v, r, s := tx.RawSignatureValues()
 		R, _ := uint256.FromBig(r)
 		S, _ := uint256.FromBig(s)
-		txSig.v = v.Uint64()
+		txSig.v = v
 		txSig.r = R
 		txSig.s = S
 		sbtx.txSigs = append(sbtx.txSigs, txSig)
```

### op-node/rollup/derive/span_batch_txs_test.go
```diff
@@ -349,7 +349,7 @@ func TestSpanBatchTxsRecoverV(t *testing.T) {
 			var spanBatchTxs spanBatchTxs
 			var txTypes []int
 			var txSigs []spanBatchSignature
-			var originalVs []uint64
+			var originalVs []*big.Int
 			yParityBits := new(big.Int)
 			protectedBits := new(big.Int)
 			totalLegacyTxCount := 0
@@ -371,8 +371,8 @@ func TestSpanBatchTxsRecoverV(t *testing.T) {
 				txSig.r, _ = uint256.FromBig(r)
 				txSig.s, _ = uint256.FromBig(s)
 				txSigs = append(txSigs, txSig)
-				originalVs = append(originalVs, v.Uint64())
-				yParityBit, err := convertVToYParity(v.Uint64(), int(tx.Type()))
+				originalVs = append(originalVs, v)
+				yParityBit, err := convertVToYParity(v, int(tx.Type()))
 				require.NoError(t, err)
 				yParityBits.SetBit(yParityBits, idx, yParityBit)
 			}
@@ -385,11 +385,11 @@ func TestSpanBatchTxsRecoverV(t *testing.T) {
 			err := spanBatchTxs.recoverV(chainID)
 			require.NoError(t, err)
 
-			var recoveredVs []uint64
+			var recoveredVs []*big.Int
 			for _, txSig := range spanBatchTxs.txSigs {
 				recoveredVs = append(recoveredVs, txSig.v)
 			}
-			require.Equal(t, originalVs, recoveredVs, "recovered v mismatch")
+			requireEqual(t, originalVs, recoveredVs, "recovered v mismatch")
 		})
 	}
 }
@@ -418,7 +418,7 @@ func TestSpanBatchTxsRoundTrip(t *testing.T) {
 		err = sbt2.recoverV(chainID)
 		require.NoError(t, err)
 
-		require.Equal(t, sbt, &sbt2)
+		requireEqual(t, sbt, &sbt2)
 	}
 }
 
@@ -465,7 +465,7 @@ func TestSpanBatchTxsRecoverVInvalidTxType(t *testing.T) {
 	var sbt spanBatchTxs
 
 	sbt.txTypes = []int{types.DepositTxType}
-	sbt.txSigs = []spanBatchSignature{{v: 0, r: nil, s: nil}}
+	sbt.txSigs = []spanBatchSignature{{v: big.NewInt(0), r: nil, s: nil}}
 	sbt.yParityBits = new(big.Int)
 	sbt.protectedBits = new(big.Int)
 
```

### op-node/withdrawals/utils.go
```diff
@@ -19,6 +19,7 @@ import (
 	"github.com/ethereum-optimism/optimism/op-node/bindings"
 	bindingspreview "github.com/ethereum-optimism/optimism/op-node/bindings/preview"
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
+	"github.com/ethereum-optimism/optimism/op-service/bigs"
 	"github.com/ethereum-optimism/optimism/op-service/eth"
 	"github.com/ethereum-optimism/optimism/op-supervisor/supervisor/backend/depset"
 )
@@ -130,12 +131,12 @@ func ProveWithdrawalParametersSuperRoots(
 	}
 	l2SequenceNumber := new(big.Int).SetBytes(latestGame.ExtraData[0:32])
 
-	superRoot, err := supervisorClient.SuperRootAtTimestamp(ctx, hexutil.Uint64(l2SequenceNumber.Uint64()))
+	superRoot, err := supervisorClient.SuperRootAtTimestamp(ctx, hexutil.Uint64(bigs.Uint64Strict(l2SequenceNumber)))
 	if err != nil {
 		return ProvenWithdrawalParametersSuperRoots{}, fmt.Errorf("failed to get super root: %w", err)
 	}
 
-	l2BlockNumber, err := rollupCfg.TargetBlockNumber(l2SequenceNumber.Uint64())
+	l2BlockNumber, err := rollupCfg.TargetBlockNumber(bigs.Uint64Strict(l2SequenceNumber))
 	if err != nil {
 		return ProvenWithdrawalParametersSuperRoots{}, fmt.Errorf("failed to get target block number: %w", err)
 	}
```
