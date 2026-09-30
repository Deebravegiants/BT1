# [?] feat(fibre): add validator-local promise cache to close double-spend window (#7703)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-08-20
Source: https://github.com/celestiaorg/celestia-app/commit/daa2108c4fc633c115762c55a1f68a164698e854
Type: security-commit

## Details
feat(fibre): add validator-local promise cache to close double-spend window (#7703)

Resolves
[PROTOCO-940](https://linear.app/celestia/issue/PROTOCO-940/keep-track-of-promise-state-locally)

Implements ADR-025 Option A. Between query-time ValidatePaymentPromise
and on-chain settlement, escrow balance isn't reserved, so two
concurrent promises from one signer can both pass validation against the
same AvailableBalance -> a validator-local double-spend. This adds an
in-memory, per-signer reservation cache on the query path that closes
that window.

What was done:

- x/fibre/keeper/local_promise_cache.go — sweep-based in-memory cache:
per-signer budget vs AvailableBalance, reservations idempotent by
promise hash, sweeps that drop on-chain-settled promises and recompute
budget, sweeps rate-limited to ≤1/block per failing signer, background
eviction of idle signers. Strictly off the ABCI path.
- keeper.go — nil-injectable promiseCache field + EnablePromiseCache().
- grpc_query.go — reserve after stateful validation; signature
(stateless) verified before any cache mutation, since the gRPC endpoint
is adversarial. Rejections return ResourceExhausted.
- app.go — cache enabled by default.

Additional Context:
- Budgets against AvailableBalance (excludes pending withdrawals). The
cache is therefore stricter than the chain-only total-Balance gate,
which is left unchanged — no consensus behaviour change.


Out of scope (documented tradeoffs)
- Multi-node/sentry bypass — cache is per-process; a client hitting
different instances of the same validator can bypass it. Real fix needs
a shared cache or on-chain reservation (separate ADR).
- Restart gap — in-memory only; protection rebuilds lazily on the first
sweep per signer after restart.
- Single global mutex (not per-signer) — same safety, defers only
cross-signer parallelism.


Tested in talis:

Regression check PASSED: 0 cache rejections (ResourceExhausted /
"insufficient available balance") across all 4 validators, while uploads
broadcast healthily. The cache is transparent to legitimate load.

## Patch
### app/app.go
```diff
@@ -455,12 +455,20 @@ func New(
 		app.StakingKeeper,
 	)
 
+	// The validator-local promise cache backs the ValidatePaymentPromise query to
+	// close the double-spend window.
+	enablePromiseCache := true
+	if v := appOpts.Get("fibre-promise-cache"); v != nil {
+		enablePromiseCache = cast.ToBool(v)
+	}
+
 	app.FibreKeeper = fibrekeeper.NewKeeper(
 		encodingConfig.Codec,
 		keys[fibretypes.StoreKey],
 		app.BankKeeper,
 		app.StakingKeeper,
 		govModuleAddr,
+		enablePromiseCache,
 	)
 
 	/****  Module Options ****/
```

### cmd/celestia-appd/cmd/root.go
```diff
@@ -37,6 +37,10 @@ const (
 
 	// DelayedPrecommitTimeoutFlag is a flag that can be used to override the DelayedPrecommitTimeout.
 	DelayedPrecommitTimeoutFlag = "delayed-precommit-timeout"
+
+	// FlagFibrePromiseCache toggles the validator-local fibre promise cache used
+	// by the ValidatePaymentPromise query.
+	FlagFibrePromiseCache = "fibre-promise-cache"
 )
 
 // NewRootCmd creates a new root command for celestia-appd.
@@ -151,6 +155,7 @@ func addStartFlags(startCmd *cobra.Command) {
 	startCmd.Flags().Duration(DelayedPrecommitTimeoutFlag, 0, "Override the DelayedPrecommitTimeout to control block time. Note: only for testing purposes.")
 	startCmd.Flags().Bool(FlagForceNoBBR, false, "bypass the requirement to use bbr locally")
 	startCmd.Flags().Bool(bypassOverridesFlagKey, false, "bypass all config overrides (P2P rates, mempool config, etc.). WARNING: Only use if strictly required. Using this flag may prevent your node from staying at the tip of the chain.")
+	startCmd.Flags().Bool(FlagFibrePromiseCache, true, "enable the validator-local fibre promise cache used by the ValidatePaymentPromise query. Enabled by default.")
 	addOTelMetricsFlag(startCmd)
 
 	prevPostRunE := startCmd.PostRunE
```

### x/fibre/keeper/abci_test.go
```diff
@@ -57,7 +57,7 @@ func (suite *ABCITestSuite) SetupTest() {
 	mockStakingKeeper := &MockStakingKeeper{}
 	authority := authtypes.NewModuleAddress("gov").String()
 	suite.ctx = sdk.NewContext(stateStore, cmtproto.Header{Time: time.Now().UTC()}, false, log.NewNopLogger())
-	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, suite.bankKeeper, mockStakingKeeper, authority)
+	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, suite.bankKeeper, mockStakingKeeper, authority, false)
 	suite.keeper.SetParams(suite.ctx, types.DefaultParams())
 	suite.msgServer = keeper.NewMsgServerImpl(*suite.keeper)
 }
```

### x/fibre/keeper/grpc_query.go
```diff
@@ -103,6 +103,25 @@ func (k Keeper) ValidatePaymentPromise(c context.Context, req *types.QueryValida
 	if err != nil {
 		return nil, status.Error(codes.Internal, err.Error())
 	}
+
+	// Reserve the promise against the validator-local budget to close the
+	// double-spend window between this validation and on-chain settlement.
+	if k.promiseCache != nil {
+		// The gRPC endpoint is adversarial: verify the signature before mutating the
+		// cache so a forged promise cannot poison a signer's budget.
+		if err := k.ValidatePaymentPromiseStateless(ctx, &req.Promise); err != nil {
+			return nil, status.Error(codes.InvalidArgument, err.Error())
+		}
+		hash, err := promiseHash(&req.Promise)
+		if err != nil {
+			return nil, status.Error(codes.InvalidArgument, err.Error())
+		}
+		signer := sdk.AccAddress(req.Promise.SignerPublicKey.Address()).String()
+		if err := k.promiseCache.Reserve(ctx, signer, hash, req.Promise.BlobSize, req.Promise.CreationTimestamp); err != nil {
+			return nil, status.Error(codes.ResourceExhausted, err.Error())
+		}
+	}
+
 	return &types.QueryValidatePaymentPromiseResponse{
 		IsValid:        true,
 		ExpirationTime: &expirationTime,
```

### x/fibre/keeper/keeper.go
```diff
@@ -23,17 +23,31 @@ type Keeper struct {
 	// authority is the address that has the authority to update module parameters.
 	// This is typically the governance module address.
 	authority string
+	// promiseCache, when non-nil, reserves escrow budget for accepted promises on
+	// the ValidatePaymentPromise query path to close the validator-local
+	// double-spend window. It is nil in consensus-only setups and unit tests and
+	// is never consulted from the ABCI path. See local_promise_cache.go.
+	promiseCache *LocalPromiseCache
 }
 
-// NewKeeper creates a new fibre Keeper instance
-func NewKeeper(cdc codec.Codec, storeKey storetypes.StoreKey, bankKeeper types.BankKeeper, stakingKeeper types.StakingKeeper, authority string) *Keeper {
-	return &Keeper{
+// NewKeeper creates a new fibre Keeper instance. When enableCache is true the
+// validator-local promise cache is attached here, so the field is set before the
+// keeper is ever copied by value (e.g. into the module's gRPC query server); this
+// keeps the double-spend protection from silently depending on call order. The
+// cache is a non-consensus, query-path-only dependency and is never consulted from
+// the ABCI path.
+func NewKeeper(cdc codec.Codec, storeKey storetypes.StoreKey, bankKeeper types.BankKeeper, stakingKeeper types.StakingKeeper, authority string, enableCache bool) *Keeper {
+	k := &Keeper{
 		cdc:           cdc,
 		storeKey:      storeKey,
 		bankKeeper:    bankKeeper,
 		stakingKeeper: stakingKeeper,
 		authority:     authority,
 	}
+	if enableCache {
+		k.promiseCache = NewLocalPromiseCache(k)
+	}
+	return k
 }
 
 // GetAuthority returns the fibre module's authority.
@@ -271,17 +285,20 @@ func (k Keeper) DeleteProcessedPayment(ctx sdk.Context, payment types.ProcessedP
 
 // IsPaymentPromiseProcessed returns true if a payment has been processed for the given promise.
 func (k Keeper) IsPaymentPromiseProcessed(ctx sdk.Context, promise *types.PaymentPromise) bool {
-	store := ctx.KVStore(k.storeKey)
-	pp := fibre.PaymentPromise{}
-	if err := pp.FromProto(promise); err != nil {
-		return false
-	}
-	hash, err := pp.Hash()
+	hash, err := promiseHash(promise)
 	if err != nil {
 		return false
 	}
-	key := types.ProcessedPaymentsByHashKey(hash)
-	return store.Has(key)
+	return k.IsPaymentProcessedByHash(ctx, hash)
+}
+
+// promiseHash returns the canonical hash of a payment promise.
+func promiseHash(promise *types.PaymentPromise) ([]byte, error) {
+	pp := fibre.PaymentPromise{}
+	if err := pp.FromProto(promise); err != nil {
+		return nil, err
+	}
+	return pp.Hash()
 }
 
 // IsPaymentProcessedByHash returns true if a payment has been processed for the given promise hash.
```

### x/fibre/keeper/keeper_test.go
```diff
@@ -23,6 +23,8 @@ import (
 	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
 	"github.com/stretchr/testify/require"
 	"github.com/stretchr/testify/suite"
+	"google.golang.org/grpc/codes"
+	"google.golang.org/grpc/status"
 )
 
 type KeeperTestSuite struct {
@@ -31,6 +33,13 @@ type KeeperTestSuite struct {
 	ctx    sdk.Context
 	keeper *keeper.Keeper
 	cdc    codec.Codec
+
+	// constructor inputs, retained so a test can rebuild the keeper with the
+	// promise cache enabled.
+	storeKey      storetypes.StoreKey
+	bankKeeper    types.BankKeeper
+	stakingKeeper types.StakingKeeper
+	authority     string
 }
 
 func TestKeeperTestSuite(t *testing.T) {
@@ -54,7 +63,8 @@ func (suite *KeeperTestSuite) SetupTest() {
 	authority := authtypes.NewModuleAddress("gov").String()
 	suite.ctx = sdk.NewContext(stateStore, cmtproto.Header{ChainID: "test-chain", Time: time.Now().UTC(), Height: 100}, false, nil)
 	mockStakingKeeper := &MockStakingKeeper{}
-	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, mockBankKeeper, mockStakingKeeper, authority)
+	suite.storeKey, suite.bankKeeper, suite.stakingKeeper, suite.authority = storeKey, mockBankKeeper, mockStakingKeeper, authority
+	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, mockBankKeeper, mockStakingKeeper, authority, false)
 	suite.keeper.SetParams(suite.ctx, types.DefaultParams())
 }
 
@@ -715,6 +725,67 @@ func (suite *KeeperTestSuite) TestValidatePaymentPromiseQueryReturnsShardRetenti
 	})
 }
 
+// twoPromisesFundedForOne returns two distinct promises from the same signer
+// whose escrow account is funded for exactly one of them, i.e. the second
+// promise is a double-spend attempt.
+func (suite *KeeperTestSuite) twoPromisesFundedForOne() (types.PaymentPromise, types.PaymentPromise) {
+	privKey := secp256k1.GenPrivKey()
+	pubKey := *privKey.PubKey().(*secp256k1.PubKey)
+
+	newPromise := func(commitmentByte byte) types.PaymentPromise {
+		p := types.PaymentPromise{
+			ChainId:           "test-chain",
+			Height:            suite.ctx.BlockHeight(),
+			Namespace:         share.MustNewV0Namespace(bytes.Repeat([]byte{0x1}, share.NamespaceVersionZeroIDSize)).Bytes(),
+			BlobSize:          uint32(1000),
+			BlobVersion:       0,
+			Commitment:        bytes.Repeat([]byte{commitmentByte}, 32),
+			CreationTimestamp: time.Now().UTC().Truncate(time.Second),
+			SignerPublicKey:   pubKey,
+			Signature:         make([]byte, 64),
+		}
+		return *suite.signPaymentPromise(&p, privKey)
+	}
+
+	promise1 := newPromise(0x01)
+	promise2 := newPromise(0x02)
+	suite.createEscrowAccount(promise1)
+	return promise1, promise2
+}
+
+// TestValidatePaymentPromiseWithoutCacheAllowsDoubleSpend is a negative control:
+// it documents the double-spend window that the cache exists to close. Without
+// the cache, two promises from a signer funded for only one both pass validation.
+func (suite *KeeperTestSuite) TestValidatePaymentPromiseWithoutCacheAllowsDoubleSpend() {
+	promise1, promise2 := suite.twoPromisesFundedForOne()
+
+	_, err := suite.keeper.ValidatePaymentPromise(suite.ctx, &types.QueryValidatePaymentPromiseRequest{Promise: promise1})
+	suite.NoError(err)
+
+	// The second promise also passes: neither validation reserved the balance.
+	_, err = suite.keeper.ValidatePaymentPromise(suite.ctx, &types.QueryValidatePaymentPromiseRequest{Promise: promise2})
+	suite.NoError(err)
+}
+
+func (suite *KeeperTestSuite) TestValidatePaymentPromiseCacheRejectsDoubleSpend() {
+	// Rebuild the keeper with the promise cache enabled; it shares the same store.
+	suite.keeper = keeper.NewKeeper(suite.cdc, suite.storeKey, suite.bankKeeper, suite.stakingKeeper, suite.authority, true)
+
+	promise1, promise2 := suite.twoPromisesFundedForOne()
+
+	_, err := suite.keeper.ValidatePaymentPromise(suite.ctx, &types.QueryValidatePaymentPromiseRequest{Promise: promise1})
+	suite.NoError(err)
+
+	// A second concurrent promise from the same signer exceeds the reserved budget.
+	_, err = suite.keeper.ValidatePaymentPromise(suite.ctx, &types.QueryValidatePaymentPromiseRequest{Promise: promise2})
+	suite.Error(err)
+	suite.Equal(codes.ResourceExhausted, status.Code(err))
+
+	// Re-submitting the first promise is idempotent (already reserved).
+	_, err = suite.keeper.ValidatePaymentPromise(suite.ctx, &types.QueryValidatePaymentPromiseRequest{Promise: promise1})
+	suite.NoError(err)
+}
+
 func (suite *KeeperTestSuite) TestValidatePaymentPromiseStatefulForTimeout() {
 	suite.T().Run("timeout mechanism should accept promise height outside window", func(t *testing.T) {
 		paymentPromise := suite.createPaymentPromise()
```

### x/fibre/keeper/local_promise_cache.go
```diff
@@ -0,0 +1,239 @@
+package keeper
+
+import (
+	"encoding/hex"
+	"fmt"
+	"sync"
+	"time"
+
+	"cosmossdk.io/math"
+	"github.com/celestiaorg/celestia-app/v10/x/fibre/types"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+)
+
+const (
+	// promiseCacheStaleAfter is how long a signer's cached budget may go
+	// unrefreshed, with at least one reservation since the last sweep, before a
+	// sweep is forced on the next reservation.
+	promiseCacheStaleAfter = time.Hour
+	// promiseCacheEvictBuffer is added to the maximum settleability window to
+	// decide when an idle signer entry may be evicted, i.e. once every promise it
+	// could hold has certainly stopped being settleable on-chain.
+	promiseCacheEvictBuffer = time.Hour
+	// promiseCacheEvictInterval is the minimum time between lazy idle-entry sweeps
+	// on the query path.
+	promiseCacheEvictInterval = 10 * time.Minute
+)
+
+// promiseStateReader is the read-only committed chain state a sweep needs to
+// reconcile cached budgets against the chain. The keeper satisfies it.
+type promiseStateReader interface {
+	GetEscrowAccount(ctx sdk.Context, signer string) (types.EscrowAccount, bool)
+	IsPaymentProcessedByHash(ctx sdk.Context, promiseHash []byte) bool
+	GetParams(ctx sdk.Context) types.Params
+}
+
+// LocalPromiseCache is a validator-local, in-memory reservation cache for fibre
+// payment promises. It closes the double-spend window between query-time
+// validation and on-chain settlement by tracking, per signer, how much of the
+// escrow AvailableBalance is already committed to promises this validator has
+// accepted but that have not yet settled on-chain.
+//
+// INVARIANT: this cache must never be reachable from the ABCI/consensus path
+// (PrepareProposal, ProcessProposal, FinalizeBlock, message servers). It is used
+// only from the ValidatePaymentPromise gRPC query. It intentionally relies on
+// wall-clock time and map iteration, neither of which is permitted in state
+// transitions; wiring it into a consensus path would violate determinism.
+type LocalPromiseCache struct {
+	reader promiseStateReader
+
+	// budgets and pending are best-effort validator-local memory with no global cap.
+	// Per signer they are bounded by the escrow budget (every reservation costs at
+	// least the fixed PayForFibre gas), and idle signers are reclaimed by eviction,
+	// so total memory scales only with the number of funded escrow accounts seen.
+	mu      sync.Mutex
+	budgets map[string]*signerBudget
+	pending map[string]pendingPromise // key: hex(promiseHash)
+	// lastEvict is when idle entries were last swept; eviction runs lazily on the
+	// query path at most once per promiseCacheEvictInterval.
+	lastEvict time.Time
+}
+
+// signerBudget is the cached budget state for a single escrow account.
+type signerBudget struct {
+	// remaining is the AvailableBalance from the last sweep minus the sum of
+	// amounts reserved for pending promises.
+	remaining math.Int
+	// lastSweep is when this budget was last reconciled against chain state.
+	lastSweep time.Time
+	// lastActivity is when this entry was last touched; drives eviction.
+	lastActivity time.Time
+	// opsSinceSweep counts reservations since the last sweep; drives staleness.
+	opsSinceSweep int
+	// lastFailSweepH is the block height of the last sweep triggered by a failing
+	// reservation; used to rate-limit sweeps for insufficient-balance signers.
+	lastFailSweepH int64
+	// hashes is the set of hex-encoded promise hashes reserved for this signer.
+	hashes map[string]struct{}
+}
+
+// pendingPromise is a reservation that has not yet settled on-chain.
+type pendingPromise struct {
+	blobSize uint32
+	// creationTimestamp is the promise's declared creation time. A sweep drops the
+	// reservation once creationTimestamp+WithdrawalDelay has passed, since the
+	// promise can no longer settle on-chain past its freshness window.
+	creationTimestamp time.Time
+}
+
+// NewLocalPromiseCache creates an empty cache backed by the given state reader.
+func NewLocalPromiseCache(reader promiseStateReader) *LocalPromiseCache {
+	return &LocalPromiseCache{
+		reader:  reader,
+		budgets: make(map[string]*signerBudget),
+		pending: make(map[string]pendingPromise),
+	}
+}
+
+// Reserve records a reservation for an accepted promise against the signer's
+// cached budget, returning an error if the remaining budget is insufficient.
+// Reservations are idempotent by promise hash.
+//
+// Callers MUST have already run stateless (signature) and stateful validation.
+// The gRPC endpoint is adversarial, so signature verification must precede any
+// cache mutation to prevent budget poisoning.
+func (c *LocalPromiseCache) Reserve(ctx sdk.Context, signer string, promiseHash []byte, blobSize uint32, creationTimestamp time.Time) error {
+	key := hex.EncodeToString(promiseHash)
+	required := requiredAmount(blobSize)
+
+	c.mu.Lock()
+	defer c.mu.Unlock()
+
+	// Reclaim idle entries lazily on the query path, at most once per interval.
+	if time.Since(c.lastEvict) > promiseCacheEvictInterval {
+		c.evictIdleLocked()
+		c.lastEvict = time.Now()
+	}
+
+	if _, ok := c.pending[key]; ok {
+		return nil // idempotent: already reserved
+	}
+
+	b, ok := c.budgets[signer]
+	if !ok {
+		b = c.sweep(ctx, signer)
+	} else if isStale(b) {
+		c.sweep(ctx, signer)
+	}
+
+	if b.remaining.GTE(required) {
+		c.reserve(b, key, blobSize, required, creationTimestamp)
+		return nil
+	}
+
+	// Insufficient budget: re-sweep at most once per block for a failing signer to
+	// reconcile with any settlements, then retry. This bounds state reads under
+	// repeated failing submissions.
+	if b.lastFailSweepH < ctx.BlockHeight() {
+		c.sweep(ctx, signer)
+		b.lastFailSweepH = ctx.BlockHeight()
+		if b.remaining.GTE(required) {
+			c.reserve(b, key, blobSize, required, creationTimestamp)
+			return nil
+		}
+	}
+
+	return fmt.Errorf("insufficient available balance for signer %s: required %s, remaining %s", signer, required, b.remaining)
+}
+
+// reserve commits a reservation to the given budget. Callers must hold c.mu.
+func (c *LocalPromiseCache) reserve(b *signerBudget, key string, blobSize uint32, required math.Int, creationTimestamp time.Time) {
+	b.remaining = b.remaining.Sub(required)
+	b.opsSinceSweep++
+	b.lastActivity = time.Now()
+	b.hashes[key] = struct{}{}
+	c.pending[key] = pendingPromise{blobSize: blobSize, creationTimestamp: creationTimestamp}
+}
+
+// sweep reconciles a signer's cached budget against committed chain state: it
+// re-reads AvailableBalance, drops any locally pending promise that has already
+// settled on-chain or that can no longer settle (past its freshness window), and
+// recomputes the remaining budget. It creates the entry if absent and returns it.
+// Callers must hold c.mu.
+func (c *LocalPromiseCache) sweep(ctx sdk.Context, signer string) *signerBudget {
+	b, ok := c.budgets[signer]
+	if !ok {
+		b = &signerBudget{hashes: make(map[string]struct{})}
+		c.budgets[signer] = b
+	}
+
+	// Reserve against AvailableBalance, not the total Balance the on-chain gate uses
+	// (validatePaymentPromiseStatefulInternal, which may settle by cancelling pending
+	// withdrawals). AvailableBalance <= Balance, so the cache is deliberately stricter
+	// than the chain: it can never admit more promises than can settle, keeping the
+	// double-spend window closed. The accepted cost is that a signer withdrawing most
+	// of its balance may be rejected here even though on-chain settlement would succeed.
+	available := math.ZeroInt()
+	if acc, found := c.reader.GetEscrowAccount(ctx, signer); found {
+		available = acc.AvailableBalance.Amount
+	}
+
+	// A promise stops being settleable on-chain once its creation_timestamp falls
+	// before current_time - WithdrawalDelay (see validatePaymentPromiseStatefulInternal).
+	// Past that cutoff its reservation can never settle, so drop it to free the
+	// budget rather than leaking it until eviction. Using WithdrawalDelay directly is
+	// conservative: the on-chain freshness floor only ever shortens this window.
+	staleBefore := ctx.BlockTime().Add(-c.reader.GetParams(ctx).WithdrawalDelay)
+
+	committed := math.ZeroInt()
+	for key := range b.hashes {
+		hash, err := hex.DecodeString(key)
+		if err != nil || c.reader.IsPaymentProcessedByHash(ctx, hash) || !c.pending[key].creationTimestamp.After(staleBefore) {
+			delete(b.hashes, key)
+			delete(c.pending, key)
+			continue
+		}
+		committed = committed.Add(requiredAmount(c.pending[key].blobSize))
+	}
+
+	remaining := available.Sub(committed)
+	if remaining.IsNegative() {
+		remaining = math.ZeroInt()
+	}
+	b.remaining = remaining
+	b.lastSweep = time.Now()
+	b.lastActivity = time.Now()
+	b.opsSinceSweep = 0
+	return b
+}
+
+// evictIdleLocked removes signer entries with no activity for longer than the
+// maximum settleability window (MaxWithdrawalDelay) plus a buffer, by when any
+// promise the entry could hold has certainly stopped being settleable on-chain.
+// Bounding on MaxWithdrawalDelay (not MaxPaymentPromiseTimeout) is required: a
+// promise stays settleable via the timeout path until creation_timestamp+
+// WithdrawalDelay, so a shorter threshold could evict a still-live reservation and
+// reopen the double-spend window. Evicted signers are rebuilt lazily on their next
+// validation. Callers must hold c.mu.
+func (c *LocalPromiseCache) evictIdleLocked() {
+	threshold := types.MaxWithdrawalDelay + promiseCacheEvictBuffer
+	for signer, b := range c.budgets {
+		if time.Since(b.lastActivity) > threshold {
+			for key := range b.hashes {
+				delete(c.pending, key)
+			}
+			delete(c.budgets, signer)
+		}
+	}
+}
+
+// isStale reports whether a budget has diverged enough from chain state to force
+// a sweep before the next reservation.
+func isStale(b *signerBudget) bool {
+	return b.opsSinceSweep > 0 && time.Since(b.lastSweep) > promiseCacheStaleAfter
+}
+
+// requiredAmount is the escrow amount a promise for the given blob size reserves.
+func requiredAmount(blobSize uint32) math.Int {
+	return math.NewIntFromUint64(EstimateGasForPayForFibre(blobSize))
+}
```

### x/fibre/keeper/local_promise_cache_test.go
```diff
@@ -0,0 +1,185 @@
+package keeper
+
+import (
+	"encoding/hex"
+	"testing"
+	"time"
+
+	"cosmossdk.io/math"
+	"github.com/celestiaorg/celestia-app/v10/pkg/appconsts"
+	"github.com/celestiaorg/celestia-app/v10/x/fibre/types"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/stretchr/testify/require"
+)
+
+// fakeStateReader is an in-memory promiseStateReader for cache tests. It ignores
+// the sdk.Context; the cache only uses it for block height.
+type fakeStateReader struct {
+	available       map[string]math.Int // signer -> AvailableBalance amount
+	processed       map[string]bool     // hex(hash) -> processed on-chain
+	escrowGets      int                 // counts GetEscrowAccount calls (sweeps)
+	withdrawalDelay time.Duration       // params.WithdrawalDelay; defaults if zero
+}
+
+func (f *fakeStateReader) GetEscrowAccount(_ sdk.Context, signer string) (types.EscrowAccount, bool) {
+	f.escrowGets++
+	amt, ok := f.available[signer]
+	if !ok {
+		return types.EscrowAccount{}, false
+	}
+	return types.EscrowAccount{
+		Signer:           signer,
+		AvailableBalance: sdk.NewCoin(appconsts.BondDenom, amt),
+	}, true
+}
+
+func (f *fakeStateReader) IsPaymentProcessedByHash(_ sdk.Context, hash []byte) bool {
+	return f.processed[hex.EncodeToString(hash)]
+}
+
+func (f *fakeStateReader) GetParams(_ sdk.Context) types.Params {
+	delay := f.withdrawalDelay
+	if delay == 0 {
+		delay = types.DefaultWithdrawalDelay
+	}
+	return types.Params{WithdrawalDelay: delay}
+}
+
+// gas for a zero-size blob; used to size test balances.
+var zeroBlobGas = math.NewIntFromUint64(EstimateGasForPayForFibre(0))
+
+func ctxAtHeight(h int64) sdk.Context { return sdk.Context{}.WithBlockHeight(h) }
+
+// promiseTS is a fixed, fresh promise creation time. The test contexts use a zero
+// block time, so any real timestamp stays within the settleability window.
+var promiseTS = time.Unix(1_000_000, 0).UTC()
+
+func TestReserveWithinBudget(t *testing.T) {
+	r := &fakeStateReader{available: map[string]math.Int{"a": zeroBlobGas.MulRaw(2)}}
+	c := NewLocalPromiseCache(r)
+
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	require.Equal(t, zeroBlobGas, c.budgets["a"].remaining)
+}
+
+func TestReserveDoubleSpendRejected(t *testing.T) {
+	r := &fakeStateReader{available: map[string]math.Int{"a": zeroBlobGas}}
+	c := NewLocalPromiseCache(r)
+
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	err := c.Reserve(ctxAtHeight(1), "a", []byte{0x02}, 0, promiseTS)
+	require.ErrorContains(t, err, "insufficient available balance")
+	require.True(t, c.budgets["a"].remaining.IsZero())
+}
+
+func TestReserveIdempotent(t *testing.T) {
+	r := &fakeStateReader{available: map[string]math.Int{"a": zeroBlobGas.MulRaw(2)}}
+	c := NewLocalPromiseCache(r)
+
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	// Budget is decremented once despite two identical submissions.
+	require.Equal(t, zeroBlobGas, c.budgets["a"].remaining)
+}
+
+func TestSweepDropsProcessed(t *testing.T) {
+	r := &fakeStateReader{
+		available: map[string]math.Int{"a": zeroBlobGas.MulRaw(2)},
+		processed: map[string]bool{},
+	}
+	c := NewLocalPromiseCache(r)
+
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	require.Equal(t, zeroBlobGas, c.budgets["a"].remaining)
+
+	// The promise settles on-chain; a sweep should drop it and free its budget.
+	r.processed[hex.EncodeToString([]byte{0x01})] = true
+	c.mu.Lock()
+	c.sweep(ctxAtHeight(1), "a")
+	c.mu.Unlock()
+
+	require.Equal(t, zeroBlobGas.MulRaw(2), c.budgets["a"].remaining)
+	require.Empty(t, c.pending)
+}
+
+func TestFailingSweepsRateLimited(t *testing.T) {
+	r := &fakeStateReader{available: map[string]math.Int{"a": math.ZeroInt()}}
+	c := NewLocalPromiseCache(r)
+
+	// First failing reservation at height 1: initial sweep + one rate-limited
+	// retry sweep = 2 reads.
+	require.Error(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+	require.Equal(t, 2, r.escrowGets)
+
+	// Second failing reservation in the same block: no further sweep.
+	require.Error(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x02}, 0, promiseTS))
+	require.Equal(t, 2, r.escrowGets)
+
+	// New block: one more retry sweep is allowed.
+	require.Error(t, c.Reserve(ctxAtHeight(2), "a", []byte{0x03}, 0, promiseTS))
+	require.Equal(t, 3, r.escrowGets)
+}
+
+func TestConcurrentReserveNoOversubscribe(t *testing.T) {
+	const budgetUnits = 5
+	const promises = 50
+	r := &fakeStateReader{available: map[string]math.Int{"a": zeroBlobGas.MulRaw(budgetUnits)}}
+	c := NewLocalPromiseCache(r)
+
+	results := make(chan error, promises)
+	for i := range promises {
+		go func(i int) {
+			results <- c.Reserve(ctxAtHeight(1), "a", []byte{byte(i)}, 0, promiseTS)
+		}(i)
+	}
+
+	ok := 0
+	for range promises {
+		if <-results == nil {
+			ok++
+		}
+	}
+	// Exactly budgetUnits reservations may succeed; the rest must be rejected.
+	require.Equal(t, budgetUnits, ok)
+	require.True(t, c.budgets["a"].remaining.IsZero())
+}
+
+func TestEvictIdle(t *testing.T) {
+	r := &fakeStateReader{available: map[string]math.Int{"a": zeroBlobGas.MulRaw(2)}}
+	c := NewLocalPromiseCache(r)
+
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, promiseTS))
+
+	// Backdate activity beyond the eviction threshold.
+	c.budgets["a"].lastActivity = time.Now().Add(-(types.MaxWithdrawalDelay + 2*time.Hour))
+	c.evictIdleLocked()
+
+	require.Empty(t, c.budgets)
+	require.Empty(t, c.pending)
+}
+
+// TestSweepDropsExpired verifies that a sweep frees a reservation once the promise
+// can no longer settle on-chain (past creation_timestamp+WithdrawalDelay), even
+// though it never settled. This prevents an abandoned promise from permanently
+// shrinking a signer's cached budget.
+func TestSweepDropsExpired(t *testing.T) {
+	r := &fakeStateReader{
+		available:       map[string]math.Int{"a": zeroBlobGas.MulRaw(2)},
+		withdrawalDelay: 24 * time.Hour,
+	}
+	c := NewLocalPromiseCache(r)
+
+	created := time.Unix(1_000_000, 0).UTC()
+	require.NoError(t, c.Reserve(ctxAtHeight(1), "a", []byte{0x01}, 0, created))
+	require.Equal(t, zeroBlobGas, c.budgets["a"].remaining)
+
+	// A block whose time is past the promise's settleability window; the reservation
+	// can never settle, so the sweep must drop it and restore the full budget.
+	ctx := ctxAtHeight(2).WithBlockTime(created.Add(25 * time.Hour))
+	c.mu.Lock()
+	c.sweep(ctx, "a")
+	c.mu.Unlock()
+
+	require.Equal(t, zeroBlobGas.MulRaw(2), c.budgets["a"].remaining)
+	require.Empty(t, c.pending)
+}
```

### x/fibre/keeper/msg_server_test.go
```diff
@@ -64,7 +64,7 @@ func (suite *MsgServerTestSuite) SetupTest() {
 	suite.stakingKeeper = &MockStakingKeeper{}
 	suite.authority = authtypes.NewModuleAddress("gov").String()
 	suite.ctx = sdk.NewContext(stateStore, cmtproto.Header{ChainID: "test-chain", Time: time.Now().UTC(), Height: 100}, false, nil)
-	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, suite.bankKeeper, suite.stakingKeeper, suite.authority)
+	suite.keeper = keeper.NewKeeper(suite.cdc, storeKey, suite.bankKeeper, suite.stakingKeeper, suite.authority, false)
 	suite.keeper.SetParams(suite.ctx, types.DefaultParams())
 	suite.msgServer = keeper.NewMsgServerImpl(*suite.keeper)
 }
```
