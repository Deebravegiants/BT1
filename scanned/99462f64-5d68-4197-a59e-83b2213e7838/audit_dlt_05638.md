# [?] db, execmoduletester: fix data race in EnableDomain vs openFolder (#20068)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-22
Source: https://github.com/erigontech/erigon/commit/2f0f3a47180a94704e98fb404cd22d7677ddca56
Type: security-commit

## Details
db, execmoduletester: fix data race in EnableDomain vs openFolder (#20068)

## Summary

- Fix flaky `race-tests / tests-linux (core-rpc)` CI failure caused by a
data race between `Aggregator.EnableDomain()` and
`Aggregator.openFolder()`
- `TestHeadStorage`, `TestBlockReceiptStorage`, and sibling tests called
`EnableDomain(kv.RCacheDomain)` **after** `execmoduletester.New(t)`
returned — racing with a background pipeline goroutine spawned by
`InsertChain` → `UpdateForkChoice` → `SnapshotsStage` →
`agg.OpenFolder()` which reads `d.Disable`
- Add `WithEnableDomain` option to `execmoduletester` so the domain is
enabled right after DB creation, before `InsertChain` spawns any
background goroutines

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### db/rawdb/accessors_chain_test.go
```diff
@@ -37,7 +37,6 @@ import (
 	"github.com/erigontech/erigon/db/kv"
 	"github.com/erigontech/erigon/db/kv/memdb"
 	"github.com/erigontech/erigon/db/rawdb"
-	"github.com/erigontech/erigon/db/state"
 	"github.com/erigontech/erigon/db/state/execctx"
 	chainspec "github.com/erigontech/erigon/execution/chain/spec"
 	"github.com/erigontech/erigon/execution/execmodule/execmoduletester"
@@ -737,8 +736,7 @@ func TestHeadStorage(t *testing.T) {
 		t.Skip("slow test")
 	}
 	t.Parallel()
-	m := execmoduletester.New(t)
-	m.DB.(state.HasAgg).Agg().(*state.Aggregator).EnableDomain(kv.RCacheDomain)
+	m := execmoduletester.New(t, execmoduletester.WithEnableDomain(kv.RCacheDomain))
 	tx, err := m.DB.BeginRw(m.Ctx)
 	require.NoError(t, err)
 	defer tx.Rollback()
@@ -765,8 +763,7 @@ func TestBlockReceiptStorage(t *testing.T) {
 		t.Skip("slow test")
 	}
 	t.Parallel()
-	m := execmoduletester.New(t)
-	m.DB.(state.HasAgg).Agg().(*state.Aggregator).EnableDomain(kv.RCacheDomain)
+	m := execmoduletester.New(t, execmoduletester.WithEnableDomain(kv.RCacheDomain))
 	tx, err := m.DB.BeginTemporalRw(m.Ctx)
 	require.NoError(t, err)
 	defer tx.Rollback()
```

### execution/execmodule/execmoduletester/exec_module_tester.go
```diff
@@ -51,6 +51,7 @@ import (
 	"github.com/erigontech/erigon/db/services"
 	"github.com/erigontech/erigon/db/snapshotsync/freezeblocks"
 	"github.com/erigontech/erigon/db/snaptype"
+	dbstate "github.com/erigontech/erigon/db/state"
 	"github.com/erigontech/erigon/execution/builder"
 	"github.com/erigontech/erigon/execution/chain"
 	"github.com/erigontech/erigon/execution/execmodule"
@@ -310,6 +311,12 @@ func WithTxPool() Option {
 	}
 }
 
+func WithEnableDomain(domain kv.Domain) Option {
+	return func(opts *options) {
+		opts.enableDomains = append(opts.enableDomains, domain)
+	}
+}
+
 func WithChainConfig(cfg *chain.Config) Option {
 	return func(opts *options) {
 		opts.chainConfig = cfg
@@ -326,6 +333,7 @@ type options struct {
 	pruneMode       *prune.Mode
 	blockBufferSize int
 	withTxPool      bool
+	enableDomains   []kv.Domain
 }
 
 func applyOptions(opts []Option) options {
@@ -426,6 +434,15 @@ func New(tb testing.TB, opts ...Option) *ExecModuleTester {
 		db = temporaltest.NewTestDB(tb, dirs)
 	}
 
+	// Enable domains before any background goroutines start (e.g. InsertChain
+	// spawns a pipeline that calls agg.OpenFolder concurrently).
+	if len(opt.enableDomains) > 0 {
+		agg := db.(dbstate.HasAgg).Agg().(*dbstate.Aggregator)
+		for _, domain := range opt.enableDomains {
+			agg.EnableDomain(domain)
+		}
+	}
+
 	if _, err := snaptype.LoadSalt(dirs.Snap, true, logger); err != nil {
 		panic(err)
 	}
```
