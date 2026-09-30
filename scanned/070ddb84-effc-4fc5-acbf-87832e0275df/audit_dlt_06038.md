# [?] fix(factory): recover panics while validating a proposed block (#4920)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-07-13
Source: https://github.com/iotexproject/iotex-core/commit/457ddbb390449703edb710fa45a16ec11c9eccb7
Type: security-commit

## Details
fix(factory): recover panics while validating a proposed block (#4920)

#4840 recovers panics on the mint path so a doomed draft cannot crash
the process. A proposed block is likewise untrusted input: extend the
same resilience to ValidateBlock so a panic while processing a block's
actions is recovered and surfaced as an error (the block is rejected)
instead of taking the validating node down. The working set is discarded
by the caller on error, so no partial state leaks and no committed state
changes; the commit/PutBlock path stays fatal as before.

Adds a regression test.

Co-authored-by: qevan <448293+guo@users.noreply.github.com>

## Patch
### state/factory/blockpreparer.go
```diff
@@ -21,8 +21,14 @@ var _mintPanicMtc = prometheus.NewCounter(prometheus.CounterOpts{
 	Help: "Number of mint goroutine panics recovered (the draft block was discarded; process kept alive).",
 })
 
+var _validateBlockPanicMtc = prometheus.NewCounter(prometheus.CounterOpts{
+	Name: "iotex_validate_block_panics_total",
+	Help: "Number of panics recovered while validating a proposed block (the block was rejected; process kept alive).",
+})
+
 func init() {
 	prometheus.MustRegister(_mintPanicMtc)
+	prometheus.MustRegister(_validateBlockPanicMtc)
 }
 
 type (
```

### state/factory/workingset.go
```diff
@@ -10,6 +10,7 @@ import (
 	"encoding/hex"
 	"fmt"
 	"math/big"
+	"runtime/debug"
 	"slices"
 	"time"
 
@@ -1073,7 +1074,24 @@ func updateReceiptIndex(receipts []*action.Receipt) {
 	}
 }
 
-func (ws *workingSet) ValidateBlock(ctx context.Context, blk *block.Block) error {
+func (ws *workingSet) ValidateBlock(ctx context.Context, blk *block.Block) (err error) {
+	// A proposed block is untrusted input. Recover any panic raised while
+	// processing its actions and reject the block instead of letting the panic
+	// kill the process — a single malformed action must not take a validating
+	// node down. The working set is discarded by the caller on error, so no
+	// partial state leaks, and no committed state changes (such a block could
+	// never validate successfully either way), so this needs no fork gate. The
+	// commit/PutBlock path (trusted data) intentionally stays fatal elsewhere.
+	defer func() {
+		if r := recover(); r != nil {
+			_validateBlockPanicMtc.Inc()
+			err = errors.Errorf("recovered from panic while validating block at height %d: %v", blk.Height(), r)
+			log.L().Error("recovered from panic while validating block; block rejected, process kept alive",
+				zap.Uint64("height", blk.Height()),
+				zap.Any("panic", r),
+				zap.String("stack", string(debug.Stack())))
+		}
+	}()
 	fCtx := protocol.MustGetFeatureCtx(ctx)
 	if fCtx.SkipSystemActionNonce {
 		if err := ws.validateNonceSkipSystemAction(ctx, blk); err != nil {
```

### state/factory/workingset_test.go
```diff
@@ -184,6 +184,58 @@ func TestWorkingSet_ValidateBlock(t *testing.T) {
 	}
 }
 
+// TestWorkingSet_ValidateBlock_RecoversPanic verifies that a panic raised while
+// processing a proposed block's actions is recovered and surfaced as an error
+// (the block is rejected) instead of crashing the validating node.
+func TestWorkingSet_ValidateBlock_RecoversPanic(t *testing.T) {
+	require := require.New(t)
+	registry := protocol.NewRegistry()
+	// a deposit-gas hook that panics stands in for any action handler that
+	// panics while processing a proposed (untrusted) block
+	panicDeposit := func(context.Context, protocol.StateManager, *big.Int, ...protocol.DepositOption) ([]*action.TransactionLog, error) {
+		panic("injected panic while processing action")
+	}
+	require.NoError(account.NewProtocol(panicDeposit).Register(registry))
+	cfg := Config{
+		Chain:   blockchain.DefaultConfig,
+		Genesis: genesis.TestDefault(),
+	}
+	cfg.Genesis.InitBalanceMap[identityset.Address(28).String()] = "100000000"
+	f, err := NewStateDB(cfg, db.NewMemKVStore(), RegistryStateDBOption(registry))
+	require.NoError(err)
+
+	startCtx := protocol.WithBlockCtx(
+		genesis.WithGenesisContext(context.Background(), cfg.Genesis),
+		protocol.BlockCtx{},
+	)
+	require.NoError(f.Start(startCtx))
+	defer func() {
+		require.NoError(f.Stop(startCtx))
+	}()
+
+	receiptRoot, _ := hash.HexStringToHash256("b8aaff4d845664a7a3f341f677365dafcdae0ae99a7fea821c7cc42c320acefe")
+	digestHash, _ := hash.HexStringToHash256("43f69c954ea0138917d69a01f7ba47da74c99cb2c6229f5969a7f0bf53efb775")
+	blk := makeBlock(t, hash.ZeroHash256, receiptRoot, digestHash, makeTransferAction(t, 1))
+
+	zctx := protocol.WithBlockCtx(context.Background(),
+		protocol.BlockCtx{
+			BlockHeight: uint64(1),
+			Producer:    identityset.Address(27),
+			GasLimit:    testutil.TestGasLimit * 100000,
+		})
+	zctx = genesis.WithGenesisContext(zctx, cfg.Genesis)
+	zctx = protocol.WithFeatureCtx(protocol.WithBlockchainCtx(zctx, protocol.BlockchainCtx{
+		ChainID: 1,
+	}))
+	zctx = protocol.WithFeatureWithHeightCtx(zctx)
+
+	// the panic must be recovered and surfaced as an error, not crash the process
+	var validateErr error
+	require.NotPanics(func() { validateErr = f.Validate(zctx, blk) })
+	require.Error(validateErr)
+	require.Contains(validateErr.Error(), "recovered from panic")
+}
+
 func TestWorkingSet_ValidateBlock_SystemAction(t *testing.T) {
 	require := require.New(t)
 	cfg := Config{
```
