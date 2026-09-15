I found the closest and strongest analog: the workflow registration global limit in `syncerlimiter.NewWorkflowLimits`. This maps directly onto the report's bug class — a shared, globally-capped resource that any unprivileged actor can register into, with no cross-tenant isolation, allowing exhaustion of capacity meant for others.

The mechanism: `syncerlimiter.Config` defines a `Global` limit (default 200, see `core/config/docs/core.toml:590-595`) shared across all workflow owners on the node, alongside a `PerOwner` limit.### Title
Unprivileged workflow owners can exhaust the node-wide global workflow-count limit, DoS-ing workflow registration for all other owners - ([File: core/services/workflows/syncerlimiter/limiter.go])

### Summary
The Chainlink CRE workflow engine enforces a per-node cap on how many workflows can run concurrently via `syncerlimiter.NewWorkflowLimits`, which combines a `PerOwner` limit and a `Global` limit (default `200` each) into a single `MultiResourcePoolLimiter`. [1](#0-0)  This mirrors the reported OpenQ bug class: a shared, globally-capped resource (there: `TOKEN_ADDRESS_LIMIT` for distinct ERC20 deposits into a bounty; here: `Global` workflow slots on a node) that is consumed on a first-come, first-served basis by any unprivileged caller, with no admission control tying consumption to a legitimate, authorized action.

### Finding Description
`syncerlimiter.Config.Global` "defines the maximum global number of workflows that can run on the node across all owners" [2](#0-1) , and is enforced by `e.cfg.GlobalWorkflowLimit.Use(ctx, 1)` in `Engine.init` every time a workflow starts. [3](#0-2)  The limiter checks both `settings.ScopeOwner` and `settings.ScopeGlobal`, and returns `ErrGlobalWorkflowCountLimitReached` when the global pool is exhausted regardless of which owner is responsible. [4](#0-3)  The `TestEngine_Start_RateLimited` test explicitly demonstrates this: with `Global=2` and `PerOwner=1`, a third, unrelated owner ("engine 4") is rejected purely because two other owners already consumed the shared global pool — not because of anything wrong with the third owner's request. [5](#0-4) 

Any address can register a workflow on-chain to the Workflow Registry (an unprivileged, permissionless action) and, once the node processes the `WorkflowRegisteredEvent`, the engine attempts to start, consuming one global slot. An attacker who creates many worthless/no-op workflow registrations (well within their own `PerOwner` allowance, e.g. up to 200 by default) can consume the entire `Global` pool (default 200) before any other legitimate owner does, causing every subsequent (legitimate) workflow activation from any other owner on that node to fail with `ErrGlobalWorkflowCountLimitReached`. [6](#0-5) 

### Impact Explanation
This is a denial-of-service on a shared, node-wide resource pool caused entirely by unprivileged/self-serve actions (on-chain workflow registration) that require no special permission. Once the global limit is reached, legitimate workflow owners on that node cannot activate their workflows until slots free up (workflow deactivation/`Free`), effectively blocking the node's workflow-execution service for everyone else — directly analogous to the reported bounty contract being DoS'd for future funders once `TOKEN_ADDRESS_LIMIT` is exhausted by worthless tokens.

### Likelihood Explanation
Likelihood is moderate-to-high in multi-tenant deployments where the `Global` limit is shared across owners that don't otherwise trust each other (default `Global = 200`, configurable via `Workflows.Limits.Global` in `core.toml`). [7](#0-6)  An attacker only needs to register up to their own `PerOwner` cap (default also 200) worth of trivial/no-op workflows to potentially consume the entire global budget, assuming they can register enough workflows before other legitimate owners fill the remaining slots. In single-tenant/permissioned deployments where all owners are trusted, the practical risk is lower, but the code itself contains no cross-owner isolation for the global pool.

### Recommendation
- Consider whether the `Global` limit is intended as a hard system safety valve (e.g., preventing resource exhaustion of the host) rather than a security boundary between mutually-untrusted owners; if the latter, add fairness/reservation mechanics (e.g., minimum guaranteed per-owner slots carved out of the global pool, or per-org quotas) so that one owner's registrations cannot starve all others.
- Ensure `PerOwnerOverrides`/org-scoped quotas are used in multi-tenant deployments to bound how much of the global pool any single owner can consume.
- Emit alerting/metrics (already partially present via `IncrementWorkflowLimitGlobalCounter`) tied to sustained global-limit exhaustion so operators can detect and mitigate abuse. [8](#0-7) 

### Proof of Concept
1. Deploy/attach to a node with default `Workflows.Limits` (`Global = 200`, `PerOwner = 200`). [7](#0-6) 
2. As an unprivileged attacker owning a single address, register up to 200 trivial workflows on the Workflow Registry contract (well within the attacker's own `PerOwner` budget).
3. As each `WorkflowRegisteredEvent` is processed, the engine calls `GlobalWorkflowLimit.Use(ctx, 1)`, consuming from the shared `Global` pool. [9](#0-8) 
4. Once 200 workflows (all from the attacker) are running, any other, legitimate owner's workflow registration/activation on the same node fails with `ErrGlobalWorkflowCountLimitReached`, as reproduced directly by `TestEngine_Start_RateLimited`'s "engine 4 gets rate-limited by global limit" subtest, where a third owner is denied purely due to the shared global cap being exhausted by unrelated owners. [10](#0-9)

### Citations

**File:** core/services/workflows/syncerlimiter/limiter.go (L16-23)
```go
type Config struct {
	// Global defines the maximum global number of workflows that can run on the node
	// across all owners.
	Global int32 `json:"global"`

	// PerOwner defines the maximum number of workflows that an owner may run.
	PerOwner int32 `json:"perOwner"`

```

**File:** core/services/workflows/syncerlimiter/limiter.go (L48-78)
```go
func NewWorkflowLimits(lggr logger.Logger, cfg Config, lf limits.Factory) (limits.ResourceLimiter[int], error) {
	lggr = logger.Named(lggr, "WorkflowExecutionLimiter")
	cfg.PerOwnerOverrides = normalizeOverrides(cfg.PerOwnerOverrides)

	ownerLimit := cresettings.Default.PerOwner.WorkflowLimit // make a copy
	if cfg.PerOwner > 0 {
		ownerLimit.DefaultValue = int(cfg.PerOwner)
	}
	perOwner := make(map[string]string, len(cfg.PerOwnerOverrides))
	for k, v := range cfg.PerOwnerOverrides {
		perOwner[k] = strconv.Itoa(int(v))
	}
	lf.Settings = keyedOwnerSettings{getter: lf.Settings, key: ownerLimit.Key, vals: perOwner}
	owner, err := limits.MakeResourcePoolLimiter(lf, ownerLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create owner resource limiter: %w", err)
	}

	globalLimit := cresettings.Default.WorkflowLimit // make a copy
	if cfg.Global > 0 {
		globalLimit.DefaultValue = int(cfg.Global)
	}
	global, err := limits.MakeResourcePoolLimiter(lf, globalLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create global resource limiter: %w", err)
	}

	lggr.Debugw("workflow limits set", "perOwner", cfg.PerOwner, "global", cfg.Global, "overrides", cfg.PerOwnerOverrides)

	return limits.MultiResourcePoolLimiter[int]{owner, global}, nil
}
```

**File:** core/services/workflows/v2/engine.go (L519-542)
```go
	// apply global engine instance limits
	// TODO(CAPPL-794): consider moving this outside of the engine, into the Syncer
	err := e.cfg.GlobalWorkflowLimit.Use(ctx, 1)
	if err != nil {
		if errLimited, ok := errors.AsType[limits.ErrorResourceLimited[int]](err); ok {
			switch errLimited.Scope {
			case settings.ScopeOwner:
				e.logger().Infow("Per owner workflow count limit reached", "err", err)
				e.metrics.IncrementWorkflowLimitPerOwnerCounter(ctx)
				e.cfg.Hooks.OnInitialized(types.ErrPerOwnerWorkflowCountLimitReached)
			case settings.ScopeGlobal:
				e.logger().Infow("Global workflow count limit reached", "err", err)
				e.metrics.IncrementWorkflowLimitGlobalCounter(ctx)
				e.cfg.Hooks.OnInitialized(types.ErrGlobalWorkflowCountLimitReached)
			default:
				e.logger().Errorw("Workflow count limit reached for unexpected scope", "scope", errLimited.Scope, "err", err)
				e.cfg.Hooks.OnInitialized(err)
			}
		} else {
			e.cfg.Hooks.OnInitialized(err)
		}
		return
	}
	e.workflowLimitUsed.Store(true)
```

**File:** core/services/workflows/v2/engine_test.go (L218-283)
```go
func TestEngine_Start_RateLimited(t *testing.T) {
	t.Parallel()
	getter, err := settings.NewTOMLGetter([]byte(`
[global]
WorkflowLimit = "2"
[global.PerOwner]
WorkflowLimit = "1"
`))
	require.NoError(t, err)
	sLimiter, err := syncerlimiter.NewWorkflowLimits(logger.Test(t), syncerlimiter.Config{
		Global:   0,
		PerOwner: 0,
	}, limits.Factory{Settings: getter})
	require.NoError(t, err)

	module := modulemocks.NewModuleV2(t)
	module.EXPECT().Start()
	module.EXPECT().Execute(matches.AnyContext, mock.Anything, mock.Anything).Return(newTriggerSubs(0), nil).Times(2)
	module.EXPECT().Close()
	capreg := regmocks.NewCapabilitiesRegistry(t)
	capreg.EXPECT().LocalNode(matches.AnyContext).Return(newNode(t), nil)
	initDoneCh := make(chan error)
	hooks := v2.LifecycleHooks{
		OnInitialized: func(err error) {
			initDoneCh <- err
		},
	}

	cfg := defaultTestConfig(t, nil)
	cfg.Module = module
	cfg.CapRegistry = capreg
	cfg.GlobalWorkflowLimit = sLimiter
	cfg.Hooks = hooks
	var engine1, engine2, engine3, engine4 *v2.Engine

	t.Run("engine 1 inits successfully", func(t *testing.T) { //nolint:paralleltest // subtests share setup
		engine1, err = v2.NewEngine(cfg)
		require.NoError(t, err)
		require.NoError(t, engine1.Start(t.Context()))
		require.NoError(t, <-initDoneCh)
	})

	t.Run("engine 2 gets rate-limited by per-owner limit", func(t *testing.T) { //nolint:paralleltest // subtests share setup
		engine2, err = v2.NewEngine(cfg)
		require.NoError(t, err)
		require.NoError(t, engine2.Start(t.Context()))
		initErr := <-initDoneCh
		require.Equal(t, types.ErrPerOwnerWorkflowCountLimitReached, initErr)
	})

	t.Run("engine 3 inits successfully", func(t *testing.T) { //nolint:paralleltest // subtests share setup
		cfg.WorkflowOwner = testWorkflowOwnerB
		engine3, err = v2.NewEngine(cfg)
		require.NoError(t, err)
		require.NoError(t, engine3.Start(t.Context()))
		require.NoError(t, <-initDoneCh)
	})

	t.Run("engine 4 gets rate-limited by global limit", func(t *testing.T) { //nolint:paralleltest // subtests share setup
		cfg.WorkflowOwner = testWorkflowOwnerC
		engine4, err = v2.NewEngine(cfg)
		require.NoError(t, err)
		require.NoError(t, engine4.Start(t.Context()))
		initErr := <-initDoneCh
		require.Equal(t, types.ErrGlobalWorkflowCountLimitReached, initErr)
	})
```

**File:** core/config/docs/core.toml (L590-596)
```text
[Workflows]
[Workflows.Limits]
# Global is the maximum number of workflows that can be registered globally.
Global = 200 # Default
# PerOwner is the maximum number of workflows that can be registered per owner.
PerOwner = 200 # Default

```
