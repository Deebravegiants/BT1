# [?] execution, cl, common/math: fix unchecked integer overflows on untrusted input (#23192)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-13
Source: https://github.com/erigontech/erigon/commit/3a8f182db1799ca1b9c1f5702fdba51e4dd0e678
Type: security-commit

## Details
execution, cl, common/math: fix unchecked integer overflows on untrusted input (#23192)

Two unchecked integer overflows in code that parses untrusted input,
found by compiling the unit suite with
[gosentry](https://github.com/trailofbits/gosentry)'s arithmetic
instrumentation (`go test -short ./...` surfaced 116 panics across 18
sites; the rest were intentional wraparound in SWAR, hashing and crypto
code).

**RIP-7560 gas limits sum without an overflow check.**
`ValidationGasLimit`, `PaymasterValidationGasLimit`, `GasLimit` and
`PostOpGasLimit` come off the wire unvalidated and were added in four
places. `chargeGas` turns the wrapped total into `preCharge` and
compares it against the payer's balance, so a wrapped-small total passes
the insufficient-funds check; `refundGas` then computes `preCharge -
actualGasCost` from the same value.

**A bitlist with no sentinel bit corrupts its hash tree root.**
`parseBitlist` reads `bits.Len8(last) - 1`; when the last byte is zero
that underflows to 255 and inflates the length mixed into the root. An
empty buffer indexed out of range.

| case | main | this PR |
| --- | --- | --- |
| `GetGasLimit()` with `ValidationGasLimit = MaxUint64` | `15000` (base
cost alone) | `MaxUint64`, checks fail closed |
| `chargeGas` / `refundGas` on an overflowing sum | wrapped total used |
rejected with `ErrGasLimitReached` |
| `BitlistRootWithLimit([]byte{0x00})` | length 255 mixed into root |
length 0 |
| `BitlistRootWithLimit([]byte{})` | `index out of range [-1]` | length
0 |

Both regression tests were confirmed to fail on unfixed code before the
fix landed.

**`SafeSub` restored.** geth's `common/math` carries `SafeAdd`,
`SafeSub` and `SafeMul`; erigon's copy dropped `SafeSub`, even though
subtraction is the most common unchecked case. Two call sites computed
the result first and detected the wrap afterwards — correct Go, but it
relies on the wraparound it is trying to reject:

| site | before | after |
| --- | --- | --- |
| `backward_beacon_downloader.go` | `slot - count + 1`, then `if start >
slot` | `math.SafeSub(slot, count-1)` |
| `txn_executor.go` | `stNonce+1 < stNonce` | `math.SafeAdd(stNonce, 1)`
|

Sites that already guard *before* subtracting (`eon_tracker.go`,
`polygon/sync`, `txpool/pool.go`) are left alone — they are correct and
converting them would be churn.

<details>
<summary>Notes for reviewers</summary>

- `GetGasLimit()` is on the `Transaction` interface and cannot return an
error, so it saturates to `MaxUint64`. That is the fail-closed
direction: gas-pool and block-gas-limit checks then reject, where a
wrapped-small value would pass. If the AA owners prefer validation to
happen strictly earlier, the helper `TotalGasLimit` is there to build
on.
- The `cl/merkle_tree` change is deliberately conservative: a bitlist
whose last byte is non-zero — every well-formed one — hashes
bit-identically to before. Only the malformed shapes change, from
garbage/panic to a defined length of 0. Rejecting malformed bitlists
outright may be more spec-correct than computing a root for them; that
is a call for the Caplin owners, and `BitlistRootWithLimit` already
returns an error if they want it.
- `TotalGasLimit` uses the existing `common/math.SafeAdd`, which carries
out via `bits.Add64` rather than adding and testing for a wrap. A
wrap-based guard is correct Go but is itself an overflow, so it trips
the same instrumentation on every future sweep.
- Verified against `./cl/merkle_tree/...`, `./execution/types` and
`./execution/protocol/...` — 9 packages, 0 failures.
- Not included: the `stage_senders.go` debug-log underflow and the
Caplin epoch-0 wrap, both of which are wrapped-then-discarded and change
no behavior.

</details>

### cl/merkle_tree/list.go
```diff
@@ -110,6 +110,10 @@ func packBitsInto(dst [][32]byte, bytes []byte) [][32]byte {
 }
 
 func parseBitlist(dst, buf []byte) ([]byte, uint64) {
+	// A bitlist without its sentinel bit has no recoverable length.
+	if len(buf) == 0 || buf[len(buf)-1] == 0 {
+		return dst, 0
+	}
 	msb := uint8(bits.Len8(buf[len(buf)-1])) - 1
 	size := uint64(8*(len(buf)-1) + int(msb))
 
```

### cl/merkle_tree/merkle_root_test.go
```diff
@@ -79,3 +79,20 @@ func TestProgressiveContainerProofRejectsOversizedSchema(t *testing.T) {
 	_, err := merkle_tree.ProgressiveContainerProofAll(0, schema...)
 	require.Error(t, err)
 }
+
+func TestBitlistRootWithLimitNoSentinel(t *testing.T) {
+	const limit = 2048
+
+	empty, err := merkle_tree.BitlistRootWithLimit([]byte{}, limit)
+	require.NoError(t, err)
+
+	for _, malformed := range [][]byte{{0x00}, {0xff, 0x00}} {
+		root, err := merkle_tree.BitlistRootWithLimit(malformed, limit)
+		require.NoError(t, err)
+		require.Equal(t, empty, root)
+	}
+
+	wellFormed, err := merkle_tree.BitlistRootWithLimit([]byte{0x03}, limit)
+	require.NoError(t, err)
+	require.NotEqual(t, empty, wellFormed)
+}
```

### cl/phase1/network/backward_beacon_downloader.go
```diff
@@ -21,7 +21,6 @@ import (
 	"errors"
 	"fmt"
 	"io"
-	"math"
 	"net/http"
 	"slices"
 	"strings"
@@ -38,6 +37,7 @@ import (
 	"github.com/erigontech/erigon/cl/sentinel/peers"
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/common/math"
 	"github.com/erigontech/erigon/db/kv"
 	"github.com/erigontech/erigon/db/snapshotsync/freezeblocks"
 )
@@ -199,8 +199,8 @@ func (b *BackwardBeaconDownloader) RequestMore(ctx context.Context) error {
 // Falls back to the beacon API when P2P is unavailable and an HTTP URL is configured.
 func (b *BackwardBeaconDownloader) fetchBlockRange(ctx context.Context) ([]*cltypes.SignedBeaconBlock, error) {
 	const count = uint64(64)
-	start := b.slotToDownload.Load() - count + 1
-	if start > b.slotToDownload.Load() { // overflow check
+	start, underflow := math.SafeSub(b.slotToDownload.Load(), count-1)
+	if underflow {
 		start = 0
 	}
 
```

### common/math/integer.go
```diff
@@ -125,6 +125,12 @@ func SafeAdd(x, y uint64) (uint64, bool) {
 	return sum, carryOut != 0
 }
 
+// SafeSub returns x-y and checks for underflow.
+func SafeSub(x, y uint64) (uint64, bool) {
+	diff, borrowOut := bits.Sub64(x, y, 0)
+	return diff, borrowOut != 0
+}
+
 // NextPowerOfTwo returns the least power of two at or above n, and 1 for
 // n == 0; n above 1<<63 wraps to 0.
 func NextPowerOfTwo(n uint64) uint64 {
```

### common/math/integer_test.go
```diff
@@ -99,3 +99,20 @@ func TestNextPowerOfTwo(t *testing.T) {
 		assert.Equal(t, tc.want, NextPowerOfTwo(tc.in), "n=%d", tc.in)
 	}
 }
+
+func TestSafeSub(t *testing.T) {
+	for _, tc := range []struct {
+		x, y, want uint64
+		underflow  bool
+	}{
+		{9, 4, 5, false},
+		{4, 4, 0, false},
+		{0, 1, ^uint64(0), true},
+		{4, 9, ^uint64(0) - 4, true},
+		{^uint64(0), ^uint64(0), 0, false},
+	} {
+		got, underflow := SafeSub(tc.x, tc.y)
+		assert.Equal(t, tc.want, got, "%d-%d", tc.x, tc.y)
+		assert.Equal(t, tc.underflow, underflow, "%d-%d", tc.x, tc.y)
+	}
+}
```

### execution/execmodule/notification_dispatcher.go
```diff
@@ -21,6 +21,7 @@ import (
 
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/common/math"
 	"github.com/erigontech/erigon/db/kv"
 	"github.com/erigontech/erigon/db/rawdb"
 	"github.com/erigontech/erigon/db/state/execctx"
@@ -109,9 +110,13 @@ func (d *Dispatcher) Dispatch(
 			// Genesis (block 0): notify from block 0.
 			notifyFrom = 0
 		default:
-			heightSpan := min(finishProgressAfter-finishProgressBefore, 1024)
-			notifyFrom = finishProgressAfter - heightSpan
-			notifyFrom++
+			// finishProgressAfter can trail finishProgressBefore, and a wrapped
+			// span would clamp to 1024 and notify over a range that never ran.
+			span, underflow := math.SafeSub(finishProgressAfter, finishProgressBefore)
+			if underflow {
+				span = 0
+			}
+			notifyFrom = finishProgressAfter - min(span, 1024) + 1
 		}
 		notifyTo := finishProgressAfter + 1 //[from, to)
 
```

### execution/protocol/aa/aa_exec.go
```diff
@@ -64,7 +64,7 @@ func ValidateAATransaction(
 	}
 	validationGasUsed = preTxCost
 
-	if err := chargeGas(header, tx, gasPool, ibs, preTxCost); err != nil {
+	if err := chargeGas(header, tx, gasPool, ibs); err != nil {
 		return nil, 0, err
 	}
 
@@ -317,7 +317,11 @@ func ExecuteAATransaction(
 		return 0, 0, err
 	}
 
-	gasPool.AddGas(params.TxAAGas + tx.ValidationGasLimit + tx.PaymasterValidationGasLimit + tx.GasLimit + tx.PostOpGasLimit - gasUsed)
+	totalGasLimit, ok := tx.TotalGasLimit(params.TxAAGas)
+	if !ok {
+		return 0, 0, fmt.Errorf("%w: RIP-7560 gas limits sum overflows uint64", protocol.ErrGasLimitReached)
+	}
+	gasPool.AddGas(totalGasLimit - gasUsed)
 
 	return executionStatus, gasUsed, nil
 }
```

### execution/protocol/aa/aa_gas.go
```diff
@@ -20,13 +20,19 @@ func chargeGas(
 	tx *types.AccountAbstractionTransaction,
 	gasPool *protocol.GasPool,
 	ibs *state.IntraBlockState,
-	preTxCost uint64,
 ) error {
 	baseFee := header.BaseFee
 	effectiveGasTip := tx.GetEffectiveGasTip(baseFee)
 	effectiveGasPrice := new(uint256.Int).Add(baseFee, &effectiveGasTip)
 
-	totalGasLimit := preTxCost + tx.ValidationGasLimit + tx.PaymasterValidationGasLimit + tx.GasLimit + tx.PostOpGasLimit
+	// RIP-7560 maxPossibleGasCost is AA_BASE_GAS_COST plus the four declared
+	// limits. preTxCost carries the dynamic calldata charges too, which the
+	// validation frame already takes out of ValidationGasLimit — charging it
+	// here would precharge more than refundGas and the gas pool ever return.
+	totalGasLimit, ok := tx.TotalGasLimit(params.TxAAGas)
+	if !ok {
+		return fmt.Errorf("%w: RIP-7560 gas limits sum overflows uint64", protocol.ErrGasLimitReached)
+	}
 	preCharge := new(uint256.Int).SetUint64(totalGasLimit)
 	preCharge = preCharge.Mul(preCharge, effectiveGasPrice)
 
@@ -62,7 +68,10 @@ func refundGas(
 	effectiveGasPrice := new(uint256.Int).Add(baseFee, &effectiveGasTip)
 	actualGasCost := new(uint256.Int).Mul(effectiveGasPrice, new(uint256.Int).SetUint64(gasUsed))
 
-	totalGasLimit := params.TxAAGas + tx.ValidationGasLimit + tx.PaymasterValidationGasLimit + tx.GasLimit + tx.PostOpGasLimit
+	totalGasLimit, ok := tx.TotalGasLimit(params.TxAAGas)
+	if !ok {
+		return fmt.Errorf("%w: RIP-7560 gas limits sum overflows uint64", protocol.ErrGasLimitReached)
+	}
 	preCharge := new(uint256.Int).SetUint64(totalGasLimit)
 	preCharge = preCharge.Mul(preCharge, effectiveGasPrice)
 
```

### execution/protocol/txn_executor.go
```diff
@@ -29,6 +29,7 @@ import (
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/dbg"
 	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/common/math"
 	"github.com/erigontech/erigon/common/u256"
 	"github.com/erigontech/erigon/execution/protocol/mdgas"
 	"github.com/erigontech/erigon/execution/protocol/params"
@@ -304,7 +305,7 @@ func (st *TxnExecutor) preCheck(gasBailout bool, intrinsicGasResult mdgas.Intrin
 			return upfrontTxnFees{}, &nonceError{err: ErrNonceTooHigh, from: from, txNonce: msgNonce, stateNonce: stNonce}
 		} else if stNonce > msgNonce {
 			return upfrontTxnFees{}, &nonceError{err: ErrNonceTooLow, from: from, txNonce: msgNonce, stateNonce: stNonce}
-		} else if stNonce+1 < stNonce {
+		} else if _, overflow := math.SafeAdd(stNonce, 1); overflow {
 			return upfrontTxnFees{}, fmt.Errorf("%w: address %v, nonce: %d", ErrNonceMax,
 				from, stNonce)
 		}
```

### execution/types/aa_transaction.go
```diff
@@ -9,6 +9,7 @@ import (
 	"github.com/holiman/uint256"
 
 	"github.com/erigontech/erigon/common"
+	"github.com/erigontech/erigon/common/math"
 	"github.com/erigontech/erigon/execution/abi"
 	"github.com/erigontech/erigon/execution/chain"
 	"github.com/erigontech/erigon/execution/protocol/mdgas"
@@ -114,8 +115,26 @@ func (tx *AccountAbstractionTransaction) GetFeeCap() *uint256.Int {
 	return tx.FeeCap
 }
 
+// TotalGasLimit reports whether base plus the declared gas limits fits in a uint64.
+func (tx *AccountAbstractionTransaction) TotalGasLimit(base uint64) (uint64, bool) {
+	total := base
+	for _, gas := range [...]uint64{tx.ValidationGasLimit, tx.PaymasterValidationGasLimit, tx.GasLimit, tx.PostOpGasLimit} {
+		sum, overflow := math.SafeAdd(total, gas)
+		if overflow {
+			return 0, false
+		}
+		total = sum
+	}
+	return total, true
+}
+
 func (tx *AccountAbstractionTransaction) GetGasLimit() uint64 {
-	return params.TxAAGas + tx.ValidationGasLimit + tx.PaymasterValidationGasLimit + tx.GasLimit + tx.PostOpGasLimit
+	// Saturate: the interface cannot report overflow, and a wrapped-small total would pass gas checks.
+	total, ok := tx.TotalGasLimit(params.TxAAGas)
+	if !ok {
+		return math.MaxUint64
+	}
+	return total
 }
 
 func (tx *AccountAbstractionTransaction) GetTipCap() *uint256.Int {
```

### execution/types/transaction_test.go
```diff
@@ -876,3 +876,18 @@ func TestTypedTxEmptyToErrorMessage(t *testing.T) {
 		})
 	}
 }
+
+func TestAATotalGasLimitOverflow(t *testing.T) {
+	t.Parallel()
+
+	tx := &AccountAbstractionTransaction{ValidationGasLimit: 1, PaymasterValidationGasLimit: 2, PostOpGasLimit: 4}
+	tx.GasLimit = 8
+	total, ok := tx.TotalGasLimit(16)
+	assert.True(t, ok)
+	assert.Equal(t, uint64(31), total)
+
+	overflowing := &AccountAbstractionTransaction{ValidationGasLimit: ^uint64(0), PaymasterValidationGasLimit: 1}
+	_, ok = overflowing.TotalGasLimit(params.TxAAGas)
+	assert.False(t, ok)
+	assert.Equal(t, ^uint64(0), overflowing.GetGasLimit())
+}
```

### node/privateapi/ethbackend.go
```diff
@@ -538,7 +538,11 @@ func (s *EthBackendServer) AAValidation(ctx context.Context, req *remoteproto.AA
 		return nil, err
 	}
 
-	totalGasLimit := preTxCost + aaTxn.ValidationGasLimit + aaTxn.PaymasterValidationGasLimit + aaTxn.GasLimit + aaTxn.PostOpGasLimit
+	totalGasLimit, ok := aaTxn.TotalGasLimit(preTxCost)
+	if !ok {
+		log.Info("RIP-7560 validation err", "err", "gas limits sum overflows uint64")
+		return &remoteproto.AAValidationReply{Valid: false}, nil
+	}
 	_, _, err = aa.ValidateAATransaction(aaTxn, ibs, new(protocol.GasPool).AddGas(totalGasLimit), header, evm, s.chainConfig)
 	if err != nil {
 		log.Info("RIP-7560 validation err", "err", err.Error())
```
