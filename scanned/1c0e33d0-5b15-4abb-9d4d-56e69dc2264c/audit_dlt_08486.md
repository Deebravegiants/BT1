# [?] fix: handle panics in epoch hooks (#894)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-06-19
Source: https://github.com/sei-protocol/sei-chain/commit/53b09514bd85b0c60268883bb491a34a1b1160dd
Type: security-commit

## Details
fix: handle panics in epoch hooks (#894)

## Patch
### utils/panic.go
```diff
@@ -2,6 +2,7 @@ package utils
 
 import (
 	"fmt"
+	"runtime/debug"
 	"strings"
 
 	"github.com/armon/go-metrics"
@@ -22,6 +23,15 @@ func PanicHandler(recoverCallback func(any)) func() {
 	}
 }
 
+// LogPanicCallback returns a callback function, given a context and a recovered
+// error value, that logs the error and a stack trace.
+func LogPanicCallback(ctx sdk.Context, r any) func(any) {
+	return func(a any) {
+		stackTrace := string(debug.Stack())
+		ctx.Logger().Error("recovered panic", "recover_err", r, "recover_type", fmt.Sprintf("%T", r), "stack_trace", stackTrace)
+	}
+}
+
 func MetricsPanicCallback(err any, ctx sdk.Context, key string) {
 	ctx.Logger().Error(fmt.Sprintf("panic %s occurred during order matching for: %s", err, key))
 	telemetry.IncrCounterWithLabels(
```

### x/epoch/module.go
```diff
@@ -168,8 +168,10 @@ func (AppModule) ConsensusVersion() uint64 { return 2 }
 func (am AppModule) BeginBlock(ctx sdk.Context, _ abci.RequestBeginBlock) {
 	lastEpoch := am.keeper.GetEpoch(ctx)
 	ctx.Logger().Info(fmt.Sprintf("Current block time %s, last %s; duration %d", ctx.BlockTime().String(), lastEpoch.CurrentEpochStartTime.String(), lastEpoch.EpochDuration))
+
 	if ctx.BlockTime().Sub(lastEpoch.CurrentEpochStartTime) > lastEpoch.EpochDuration {
 		am.keeper.AfterEpochEnd(ctx, lastEpoch)
+
 		newEpoch := types.Epoch{
 			GenesisTime:           lastEpoch.GenesisTime,
 			EpochDuration:         lastEpoch.EpochDuration,
@@ -179,13 +181,15 @@ func (am AppModule) BeginBlock(ctx sdk.Context, _ abci.RequestBeginBlock) {
 		}
 		am.keeper.SetEpoch(ctx, newEpoch)
 		am.keeper.BeforeEpochStart(ctx, newEpoch)
+
 		ctx.EventManager().EmitEvent(
 			sdk.NewEvent(types.EventTypeNewEpoch,
 				sdk.NewAttribute(types.AttributeEpochNumber, fmt.Sprint(newEpoch.CurrentEpoch)),
 				sdk.NewAttribute(types.AttributeEpochTime, newEpoch.CurrentEpochStartTime.String()),
 				sdk.NewAttribute(types.AttributeEpochHeight, fmt.Sprint(newEpoch.CurrentEpochHeight)),
 			),
 		)
+
 		metrics.SetEpochNew(newEpoch.CurrentEpoch)
 	}
 }
```

### x/epoch/types/hooks.go
```diff
@@ -2,12 +2,14 @@ package types
 
 import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/sei-protocol/sei-chain/utils"
 )
 
 type EpochHooks interface {
-	// the first block whose timestamp is after the duration is counted as the end of the epoch
+	// AfterEpochEnd defines the first block whose timestamp is after the duration
+	// is counted as the end of the epoch.
 	AfterEpochEnd(ctx sdk.Context, epoch Epoch)
-	// new epoch is next block of epoch end block
+	// BeforeEpochStart defines the new epoch is next block of epoch EndBlock.
 	BeforeEpochStart(ctx sdk.Context, epoch Epoch)
 }
 
@@ -19,16 +21,29 @@ func NewMultiEpochHooks(hooks ...EpochHooks) MultiEpochHooks {
 	return hooks
 }
 
-// AfterEpochEnd is called when epoch is going to be ended, epochNumber is the number of epoch that is ending.
+// AfterEpochEnd is called when epoch is going to be ended, epochNumber is the
+// number of epoch that is ending.
 func (h MultiEpochHooks) AfterEpochEnd(ctx sdk.Context, epoch Epoch) {
 	for i := range h {
-		h[i].AfterEpochEnd(ctx, epoch)
+		panicCatchingEpochHook(ctx, h[i].AfterEpochEnd, epoch)
 	}
 }
 
-// BeforeEpochStart is called when epoch is going to be started, epochNumber is the number of epoch that is starting.
+// BeforeEpochStart is called when epoch is going to be started, epochNumber is
+// the number of epoch that is starting.
 func (h MultiEpochHooks) BeforeEpochStart(ctx sdk.Context, epoch Epoch) {
 	for i := range h {
-		h[i].BeforeEpochStart(ctx, epoch)
+		panicCatchingEpochHook(ctx, h[i].BeforeEpochStart, epoch)
 	}
 }
+
+func panicCatchingEpochHook(ctx sdk.Context, hookFn func(sdk.Context, Epoch), epoch Epoch) {
+	defer utils.PanicHandler(func(r any) {
+		utils.LogPanicCallback(ctx, r)
+	})()
+
+	// cache the context and only write if no panic (which is caught above)
+	cacheCtx, write := ctx.CacheContext()
+	hookFn(cacheCtx, epoch)
+	write()
+}
```

### x/epoch/types/hooks_test.go
```diff
@@ -3,22 +3,34 @@ package types_test
 import (
 	"testing"
 
+	"github.com/cosmos/cosmos-sdk/store"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/sei-protocol/sei-chain/x/epoch/keeper"
 	"github.com/sei-protocol/sei-chain/x/epoch/types"
 	"github.com/stretchr/testify/require"
+	tmproto "github.com/tendermint/tendermint/proto/tendermint/types"
+	tmdb "github.com/tendermint/tm-db"
 )
 
 type mockEpochHooks struct {
 	afterEpochEndCalled    bool
 	beforeEpochStartCalled bool
+	shouldPanic            bool
 }
 
 func (h *mockEpochHooks) AfterEpochEnd(_ sdk.Context, _ types.Epoch) {
+	if h.shouldPanic {
+		panic("AfterEpochEnd")
+	}
+
 	h.afterEpochEndCalled = true
 }
 
 func (h *mockEpochHooks) BeforeEpochStart(_ sdk.Context, _ types.Epoch) {
+	if h.shouldPanic {
+		panic("BeforeEpochStart")
+	}
+
 	h.beforeEpochStartCalled = true
 }
 
@@ -45,8 +57,10 @@ func TestMultiHooks(t *testing.T) {
 		hooks,
 	}
 
-	ctx := sdk.Context{}   // setup context as required
-	epoch := types.Epoch{} // setup epoch as required
+	db := tmdb.NewMemDB()
+	ms := store.NewCommitMultiStore(db)
+	ctx := sdk.NewContext(ms, tmproto.Header{}, false, nil)
+	epoch := types.Epoch{}
 
 	multiHooks.AfterEpochEnd(ctx, epoch)
 	require.True(t, hooks.afterEpochEndCalled)
@@ -56,3 +70,24 @@ func TestMultiHooks(t *testing.T) {
 	multiHooks.BeforeEpochStart(ctx, epoch)
 	require.True(t, hooks.beforeEpochStartCalled)
 }
+
+func TestMultiHooks_Panic(t *testing.T) {
+	hook1 := &mockEpochHooks{shouldPanic: false}
+	hook2 := &mockEpochHooks{shouldPanic: true}
+	hook3 := &mockEpochHooks{shouldPanic: false}
+	multiHooks := types.MultiEpochHooks{
+		hook1,
+		hook2,
+		hook3,
+	}
+
+	db := tmdb.NewMemDB()
+	ms := store.NewCommitMultiStore(db)
+	ctx := sdk.NewContext(ms, tmproto.Header{}, false, nil)
+	epoch := types.Epoch{}
+
+	multiHooks.AfterEpochEnd(ctx, epoch)
+	require.True(t, hook1.afterEpochEndCalled)
+	require.False(t, hook2.afterEpochEndCalled) // second hook should panic
+	require.True(t, hook3.afterEpochEndCalled)  // third hook should still run after 2nd
+}
```
