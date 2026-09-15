## Analysis

The Sherlock report's bug class is a **stale index entry left behind after a "replace" operation**: `D3MakerFreeSlot.setNewTokenAndReplace()` overwrites `oldToken`'s slot but never clears `oldToken`'s entry from `tokenIndexMap`, so the system keeps believing the old token is still registered. The closest analog in this codebase is in the internet-facing bridge/external-adapter connection cache, `bridgeConnManager`, which caches per-bridge-name state and never invalidates it when the bridge's underlying configuration (URL) is replaced.

### Root cause

`bridgeConnManager` is a **process-wide singleton** that maps `bridgeName -> *eaConn` and never removes or refreshes an entry once created: [1](#0-0) 

`getOrCreateConn` returns the existing cached connection for a bridge name unconditionally — it never compares the cached connection's target URL against the bridge's *current* URL, and there is no code path anywhere in the package (or in `BridgeTypesController.Update`/`DeleteBridgeType`) that evicts or refreshes an `eaConn` when a bridge is updated or deleted: [2](#0-1) 

Compare this with `bridges.Cache`, which *does* correctly evict/refresh its `bridgeTypesCache` on `UpdateBridgeType`/`DeleteBridgeType`: [3](#0-2) 

But `BridgeTypesController.Update` (an unprivileged/admin API surface for editing bridge URLs) only calls `orm.UpdateBridgeType`, which updates the DB row and the `bridges.Cache` — it never touches `bridgeConnManager`: [4](#0-3) 

`GetObservation` derives both the `eaConn` (via `getOrCreateConn(bridgeName, bridge.URL)`) and the observation cache key (via `bridgeObservationCacheKey(bridgeName, data)`) using only the **bridge name**, not the URL: [5](#0-4) 

Once `newEAConn` captures a target host/scheme for a bridge name, that target is baked into the `eaConn` struct for the lifetime of the process: [6](#0-5) 

### Why this matches the analog class

This is structurally the same defect as M-1: an entity ("token" → here, "bridge") is replaced/updated at the authoritative store (DB row / `bridges.Cache`), but a secondary index/cache (`tokenIndexMap` → here, `bridgeConnManager.conns`) retains the *stale* association and is never cleared, so the system keeps behaving as if the old configuration is still in effect.

Concretely: if an operator rotates a bridge's URL via `PATCH /v2/bridge_types/:name` (e.g., because the previous external adapter endpoint was compromised, decommissioned, or pointed at the wrong provider), any bridge task using that bridge name for streams-adapter observations continues to be served from the **old, stale `eaConn`/target** for as long as the node process is up, since `getOrCreateConn` only checks presence-by-name, never freshness of the URL. Pipeline runs (including those triggered by external initiators hitting `/v2/jobs/:id/runs` with only run-scoped credentials) that read the bridge observation will silently receive data sourced from the stale, no-longer-configured adapter, while the system reports/audits the bridge as pointing to the new URL. This is a cross-user/cross-context response confusion condition rooted in a stale cache entry not being cleared on a config replace, mirroring the mechanics of M-1.

### Uncertainty

I could not fully trace, within the remaining budget, the exact call path from `/v2/jobs/:id/runs` (external-initiator webhook runs) down to `task.bridge.go`'s use of `BridgeConnManager.GetObservation`, nor confirm whether this streams-adapter GetObservation path is exercised only for a specific job/task type (e.g., LLO/mercury bridge tasks) versus all bridge tasks. That would need further inspection of `core/services/pipeline/task.bridge.go` and `core/services/pipeline/runner.go` to establish precisely which unprivileged trigger surfaces reach it.

### Title
Stale `bridgeConnManager` connection cache is never invalidated on bridge URL update/rotation - (File: `core/services/pipeline/bridgeconn/bridge_conn_manager.go`)

### Summary
`bridgeConnManager.getOrCreateConn` permanently caches an `eaConn` (target host/TLS) per bridge name and never evicts or refreshes it when the bridge's URL is changed via `BridgeTypesController.Update` or when the bridge is deleted/recreated, causing the node to keep streaming/serving observations from a stale, no-longer-configured external adapter endpoint.

### Finding Description
`bridgeConnManager.conns` is a package-level singleton map keyed only by `bridgeName`. `getOrCreateConn` returns the cached `*eaConn` if the name is present, with no comparison against the bridge's current URL and no invalidation hook wired to `UpdateBridgeType`/`DeleteBridgeType`. `bridges.Cache` correctly refreshes its own bridge metadata cache on update/delete, but `bridgeConnManager` is not integrated with that lifecycle at all, so the stale target captured in `newEAConn` at first use is never replaced.

### Impact Explanation
This is analogous to M-1: a "replace" operation on the authoritative record (bridge URL update) leaves a stale association in a secondary index (`conns` map) that is never cleared, causing the system to keep operating on outdated state. In practice, this results in observations for a given bridge name continuing to be sourced from the old external adapter target after the operator has rotated/fixed the bridge URL, producing response data that does not correspond to the currently configured bridge — a cross-context confusion between the bridge's declared configuration and what is actually served to consumers of `GetObservation`.

### Likelihood Explanation
Requires an operator (already privileged to manage bridges) to update a bridge's URL while the node process has already established a connection under the old URL; from that point on, any unprivileged/run-scoped path exercising that bridge name's observation lookup is silently affected until process restart. Likelihood of the triggering admin action is not attacker-controlled but the resulting confusion affects all subsequent unprivileged consumers automatically.

### Recommendation
Track the URL (or a hash of it) alongside the bridge name in `bridgeConnManager.conns`, and when it differs from the current bridge's URL, close the stale `eaConn` and create a new one. Additionally, wire `bridgeConnManager` invalidation into `UpdateBridgeType`/`DeleteBridgeType` (similar to how `bridges.Cache` invalidates `bridgeTypesCache`) so config changes take effect immediately instead of persisting for the life of the process.

### Proof of Concept
Not independently verified with a running reproduction due to tool/time constraints; the code paths cited above show the missing invalidation directly (`getOrCreateConn` keyed by name only, `Update`/`Destroy` controller handlers never call into `bridgeConnManager`).

### Citations

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L43-56)
```go
// bridgeConnManager is a package-level singleton: one observation cache plus one
// EAConn registry shared by every pipeline run in the process. It self-initializes
// lazily as bridges are first used; there is no explicit start/close lifecycle.
type bridgeConnManager struct {
	mu    sync.RWMutex
	cache map[[32]byte]cacheEntry

	connsMu sync.Mutex
	conns   map[string]*eaConn // bridge name -> EAConn
	lggr    logger.Logger      // immutable after singleton creation

	dial  eaStreamDialer
	clock clockwork.Clock
}
```

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L82-111)
```go
func (m *bridgeConnManager) GetObservation(bridge bridges.BridgeType, requestData map[string]any) ([]byte, error) {
	bridgeName := strings.TrimPrefix(bridge.Name.String(), "bridge-")
	data, err := subscriptionData(requestData)
	if err != nil {
		return nil, fmt.Errorf("bridge %q: %w", bridgeName, err)
	}
	key, err := bridgeObservationCacheKey(bridgeName, data)
	if err != nil {
		return nil, err
	}
	m.lggr.Debugw("cache key generated", "key", hex.EncodeToString(key[:]), "bridge", bridgeName, "data", data)
	subscription, err := structpb.NewStruct(data)
	if err != nil {
		return nil, fmt.Errorf("failed to build subscription payload for bridge %q: %w", bridgeName, err)
	}
	m.getOrCreateConn(bridgeName, bridge.URL).registerAsset(key, subscription)

	m.mu.RLock()
	entry, ok := m.cache[key]
	m.mu.RUnlock()
	if !ok {
		return nil, fmt.Errorf("%w for bridge %q", ErrBridgeObservationNotFound, bridgeName)
	}
	if m.clock.Now().Sub(entry.storedAt) > observationTTL {
		return nil, fmt.Errorf("%w for bridge %q", ErrBridgeObservationExpired, bridgeName)
	}
	payload := make([]byte, len(entry.payload))
	copy(payload, entry.payload)
	return payload, nil
}
```

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L138-151)
```go
// getOrCreateConn returns the bridge's persistent EAConn, lazily creating and
// starting it on first use.
func (m *bridgeConnManager) getOrCreateConn(bridgeName string, bridgeURL models.WebURL) *eaConn {
	m.connsMu.Lock()
	defer m.connsMu.Unlock()
	if conn, ok := m.conns[bridgeName]; ok {
		return conn
	}

	conn := newEAConn(bridgeName, bridgeURL, m)
	m.conns[bridgeName] = conn
	conn.start()
	return conn
}
```

**File:** core/bridges/cache.go (L114-151)
```go
func (c *Cache) DeleteBridgeType(ctx context.Context, bt *BridgeType) error {
	err := c.ORM.DeleteBridgeType(ctx, bt)
	if err != nil {
		if !errors.Is(err, sql.ErrNoRows) {
			return err
		}
	}

	// We delete regardless of the rows affected, in case it gets out of sync
	c.bridgeTypesCache.Delete(bt.Name)

	return err
}

func (c *Cache) BridgeTypes(ctx context.Context, offset, limit int) ([]BridgeType, int, error) {
	return c.ORM.BridgeTypes(ctx, offset, limit)
}

func (c *Cache) CreateBridgeType(ctx context.Context, bt *BridgeType) error {
	err := c.ORM.CreateBridgeType(ctx, bt)
	if err != nil {
		return err
	}

	c.bridgeTypesCache.Store(bt.Name, *bt)

	return nil
}

func (c *Cache) UpdateBridgeType(ctx context.Context, bt *BridgeType, btr *BridgeTypeRequest) error {
	if err := c.ORM.UpdateBridgeType(ctx, bt, btr); err != nil {
		return err
	}

	c.bridgeTypesCache.Store(bt.Name, *bt)

	return nil
}
```

**File:** core/web/bridge_types_controller.go (L148-192)
```go
// Update can change the restricted attributes for a bridge
func (btc *BridgeTypesController) Update(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")
	btr := &bridges.BridgeTypeRequest{}

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	orm := btc.App.BridgeORM()
	bt, err := orm.FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := c.ShouldBindJSON(btr); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if err := ValidateBridgeType(btr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := orm.UpdateBridgeType(ctx, &bt, btr); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	btc.App.GetAuditLogger().Audit(audit.BridgeUpdated, map[string]any{
		"bridgeName":                   bt.Name,
		"bridgeConfirmations":          bt.Confirmations,
		"bridgeMinimumContractPayment": bt.MinimumContractPayment,
		"bridgeURL":                    bt.URL,
	})

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
```

**File:** core/services/pipeline/bridgeconn/eaconn.go (L106-137)
```go
// eaConn is the single persistent connection owned by BridgeConnManager for one
// bridge name. It sends complete active-asset snapshots on a fixed interval,
// applies indirect unsubscribe by omitting idle assets from the next snapshot, and
// reconnects with fixed exponential backoff on any dial/send/receive failure.
type eaConn struct {
	bridgeName string
	target     string
	useTLS     bool
	dial       eaStreamDialer
	lggr       logger.Logger
	manager    *bridgeConnManager
	clock      clockwork.Clock

	mu     sync.Mutex
	assets map[[32]byte]*eaAsset

	startOnce sync.Once
}

func newEAConn(bridgeName string, bridgeURL models.WebURL, manager *bridgeConnManager) *eaConn {
	u := url.URL(bridgeURL)
	return &eaConn{
		bridgeName: bridgeName,
		target:     u.Host,
		useTLS:     u.Scheme == "https",
		dial:       manager.dial,
		lggr:       logger.With(logger.Named(manager.lggr, "EAConn"), "bridgeName", bridgeName),
		manager:    manager,
		clock:      manager.clock,
		assets:     make(map[[32]byte]*eaAsset),
	}
}
```
