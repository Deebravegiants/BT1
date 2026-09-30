# [?] fix(factory): evict sender when an action panics during minting (#4921)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-08-19
Source: https://github.com/iotexproject/iotex-core/commit/c2bab8df382eb88a5663f3341ec6897d3d38b71e
Type: security-commit

## Details
fix(factory): evict sender when an action panics during minting (#4921)

If a single pending action panics while runAction executes it during
minting, the panic previously unwound past the sender-eviction logic in
validateAndRun and was only caught by the mint goroutine's top-level
recover, discarding the whole draft without removing the action from
the pool. The same action would then be retried on every subsequent
mint attempt.

Recover the panic right around the single-action runAction call so it
is converted into an ordinary error and routed through the existing
default-error handling, which evicts the sender from the pool before
this draft is abandoned. This turns a potential run of repeated draft
failures into a one-time lost draft.

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>

## Patch
### state/factory/blockpreparer.go
```diff
@@ -26,9 +26,15 @@ var _validateBlockPanicMtc = prometheus.NewCounter(prometheus.CounterOpts{
 	Help: "Number of panics recovered while validating a proposed block (the block was rejected; process kept alive).",
 })
 
+var _mintActionPanicMtc = prometheus.NewCounter(prometheus.CounterOpts{
+	Name: "iotex_mint_action_panics_total",
+	Help: "Number of panics recovered while running a single action during minting (the action's sender was evicted from the pool so the next mint attempt won't retry it; this draft was still discarded).",
+})
+
 func init() {
 	prometheus.MustRegister(_mintPanicMtc)
 	prometheus.MustRegister(_validateBlockPanicMtc)
+	prometheus.MustRegister(_mintActionPanicMtc)
 }
 
 type (
```

### state/factory/workingset.go
```diff
@@ -1030,7 +1030,7 @@ func (ws *workingSet) validateAndRun(
 		log.L().Info("failed to validate tx", zap.Uint64("height", ws.height), zap.Error(err))
 		return true, true, nil, nil
 	}
-	receipt, err := ws.runAction(actionCtx, nextAction, revertAllSnapshots)
+	receipt, err := ws.runActionDuringMint(actionCtx, nextAction, revertAllSnapshots)
 	switch errors.Cause(err) {
 	case nil:
 		// do nothing
@@ -1050,6 +1050,32 @@ func (ws *workingSet) validateAndRun(
 	return false, false, receipt, nil
 }
 
+// runActionDuringMint runs a single action while assembling a draft block, recovering from
+// any panic raised in the process. A panic here otherwise unwinds past this whole draft (caught
+// only by the mint goroutine's recover in blockpreparer.go) and, unlike a normal error return,
+// skips the caller's sender-eviction logic — so the same poison action would be picked again on
+// every subsequent mint attempt, stalling block production instead of losing a single draft.
+// Converting the panic into an ordinary error routes it through validateAndRun's default case,
+// which evicts the sender from the pool before this draft is abandoned.
+func (ws *workingSet) runActionDuringMint(ctx context.Context, selp *action.SealedEnvelope, revertAllSnapshots bool) (receipt *action.Receipt, err error) {
+	defer func() {
+		if r := recover(); r != nil {
+			_mintActionPanicMtc.Inc()
+			actHash, hashErr := selp.Hash()
+			if hashErr != nil {
+				log.L().Error("failed to get action hash after recovering from mint-time panic", zap.Error(hashErr))
+			}
+			log.L().Error("recovered from panic while running action during mint; sender will be evicted from the pool",
+				log.Hex("action", actHash[:]),
+				zap.Any("panic", r),
+				zap.String("stack", string(debug.Stack())))
+			receipt = nil
+			err = errors.Errorf("recovered from panic while running action %x: %v", actHash, r)
+		}
+	}()
+	return ws.runAction(ctx, selp, revertAllSnapshots)
+}
+
 func (ws *workingSet) generateSignedSystemActions(ctx context.Context, sign func(elp action.Envelope) (*action.SealedEnvelope, error)) ([]*action.SealedEnvelope, error) {
 	unsignedSystemActions, err := ws.generateSystemActions(ctx)
 	if err != nil {
```

### state/factory/workingset_test.go
```diff
@@ -14,6 +14,9 @@ import (
 	"github.com/iotexproject/go-pkgs/hash"
 	"github.com/pkg/errors"
 	"github.com/stretchr/testify/require"
+	"go.uber.org/mock/gomock"
+
+	"github.com/iotexproject/iotex-address/address"
 
 	"github.com/iotexproject/iotex-core/v2/action"
 	"github.com/iotexproject/iotex-core/v2/action/protocol"
@@ -25,6 +28,7 @@ import (
 	"github.com/iotexproject/iotex-core/v2/db"
 	"github.com/iotexproject/iotex-core/v2/pkg/unit"
 	"github.com/iotexproject/iotex-core/v2/test/identityset"
+	"github.com/iotexproject/iotex-core/v2/test/mock/mock_actpool"
 	"github.com/iotexproject/iotex-core/v2/testutil"
 )
 
@@ -236,6 +240,70 @@ func TestWorkingSet_ValidateBlock_RecoversPanic(t *testing.T) {
 	require.Contains(validateErr.Error(), "recovered from panic")
 }
 
+// TestWorkingSet_Mint_RecoversActionPanic verifies that a panic raised while running a
+// single pending action during minting is recovered into an error (the draft is discarded,
+// same as today) and that the offending sender is evicted from the pool — so the next mint
+// attempt no longer sees the poison action, turning what would otherwise be a persistent
+// block-production stall into a one-time lost draft.
+func TestWorkingSet_Mint_RecoversActionPanic(t *testing.T) {
+	require := require.New(t)
+	registry := protocol.NewRegistry()
+	panicDeposit := func(context.Context, protocol.StateManager, *big.Int, ...protocol.DepositOption) ([]*action.TransactionLog, error) {
+		panic("injected panic while running action during mint")
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
+	selp := makeTransferAction(t, 1)
+	sender := identityset.Address(28)
+
+	ctrl := gomock.NewController(t)
+	ap := mock_actpool.NewMockActPool(ctrl)
+	ap.EXPECT().BundlePool().Return(nil).Times(1)
+	ap.EXPECT().PendingActionMap().Return(map[string][]*action.SealedEnvelope{
+		sender.String(): {selp},
+	}).Times(1)
+	ap.EXPECT().DeleteAction(gomock.Any()).Do(func(addr address.Address) {
+		require.Equal(sender.String(), addr.String())
+	}).Times(1)
+
+	ctx := protocol.WithBlockCtx(context.Background(),
+		protocol.BlockCtx{
+			BlockHeight: uint64(1),
+			Producer:    identityset.Address(27),
+			GasLimit:    testutil.TestGasLimit * 100000,
+		})
+	ctx = protocol.WithBlockchainCtx(
+		genesis.WithGenesisContext(ctx, cfg.Genesis),
+		protocol.BlockchainCtx{},
+	)
+	ctx = protocol.WithFeatureCtx(protocol.WithFeatureWithHeightCtx(ctx))
+
+	// the panic must be recovered and surfaced as an error, not crash the mint goroutine,
+	// and the poison action's sender must be evicted from the pool (see ap.EXPECT().DeleteAction above)
+	var mintErr error
+	require.NotPanics(func() {
+		_, mintErr = f.Mint(ctx, ap, identityset.PrivateKey(27))
+	})
+	require.Error(mintErr)
+	require.Contains(mintErr.Error(), "recovered from panic")
+}
+
 func TestWorkingSet_ValidateBlock_SystemAction(t *testing.T) {
 	require := require.New(t)
 	cfg := Config{
```
