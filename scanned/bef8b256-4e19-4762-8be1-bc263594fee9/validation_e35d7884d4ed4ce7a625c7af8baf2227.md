### Title
`protocolUnpausePool` Leaves Pool in Admin-Paused State Instead of Restoring Active State — (File: `metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.protocolUnpausePool` calls `setPause(1)` (admin-paused) instead of `setPause(0)` (active). A pool that was fully active before a protocol pause is left permanently paused at admin level after the protocol "unpauses" it, with no way for the protocol owner to restore it to active without pool-admin cooperation.

---

### Finding Description

The pause system uses three levels:

| Level | Meaning |
|---|---|
| 0 | Active |
| 1 | Admin-paused |
| 2 | Protocol-paused |

`protocolPausePool` accepts transitions from **both** level 0 and level 1 to level 2: [1](#0-0) 

```solidity
function protocolPausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 0 && cur != 1) revert InvalidPauseTransition(cur, 2);
    IMetricOmmPoolFactoryActions(pool).setPause(2);
}
```

`protocolUnpausePool` always transitions to level **1** (admin-paused), never to level 0 (active): [2](#0-1) 

```solidity
function protocolUnpausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 2) revert InvalidPauseTransition(cur, 1);
    IMetricOmmPoolFactoryActions(pool).setPause(1);
}
```

The function name `protocolUnpausePool` describes restoring the pool to an operational state, but the implementation leaves `pauseLevel = 1`. The pool's `whenNotPaused` modifier rejects any non-zero pause level: [3](#0-2) 

```solidity
function _checkNotPaused() internal view {
    if (pauseLevel != 0) revert PoolPaused();
}
```

Because `protocolPausePool` accepts level 0 as a valid source state, a pool that was **never** admin-paused can be driven through the cycle `0 → 2 → 1`, ending in admin-paused state that it was never in before. The protocol owner has no path to set level 0 directly; only the pool admin can call `unpausePool` (which requires `cur == 1 → 0`): [4](#0-3) 

```solidity
function unpausePool(address pool) external override nonReentrant onlyPoolAdmin(pool) {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 1) revert InvalidPauseTransition(cur, 0);
    IMetricOmmPoolFactoryActions(pool).setPause(0);
}
```

---

### Impact Explanation

After a protocol pause/unpause cycle on an active pool, swaps remain blocked (`PoolPaused`). The protocol owner — who performed the "unpause" — cannot restore the pool to active state unilaterally. If the pool admin key is lost, rotated to an unresponsive address, or the admin refuses to cooperate, the pool is permanently stuck in admin-paused state. All swap volume and LP fee accrual is lost for the duration. This matches the impact gate criterion: **broken core pool functionality causing unusable swap flows**.

---

### Likelihood Explanation

This triggers on every protocol pause/unpause cycle applied to a pool that was at level 0 (active) — the normal operational state for any live pool. No special setup is required; the protocol owner exercising their documented authority is sufficient.

---

### Recommendation

Preserve the pre-pause level and restore it on unpause, or allow the protocol owner to set level 0 directly. The simplest fix is to have `protocolUnpausePool` call `setPause(0)` and update the transition guard accordingly:

```solidity
function protocolUnpausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 2) revert InvalidPauseTransition(cur, 0);
    IMetricOmmPoolFactoryActions(pool).setPause(0); // restore to active
}
```

Alternatively, store the pre-pause level in factory state when `protocolPausePool` is called and restore it here.

---

### Proof of Concept

1. Pool is deployed and active: `pauseLevel = 0`.
2. Protocol owner calls `protocolPausePool(pool)` — allowed because `cur == 0`. Pool: `pauseLevel = 2`.
3. Protocol owner calls `protocolUnpausePool(pool)` — sets `pauseLevel = 1` (admin-paused).
4. Any user calls `swap(...)` → reverts `PoolPaused` because `pauseLevel != 0`.
5. Protocol owner has no further lever; only the pool admin can call `unpausePool` to reach level 0.
6. If `poolAdmin[pool]` is unresponsive, the pool is permanently paused despite the protocol owner having "unpaused" it.

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L392-396)
```text
  function protocolPausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 0 && cur != 1) revert InvalidPauseTransition(cur, 2);
    IMetricOmmPoolFactoryActions(pool).setPause(2);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L399-403)
```text
  function protocolUnpausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 2) revert InvalidPauseTransition(cur, 1);
    IMetricOmmPoolFactoryActions(pool).setPause(1);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L467-471)
```text
  function unpausePool(address pool) external override nonReentrant onlyPoolAdmin(pool) {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 1) revert InvalidPauseTransition(cur, 0);
    IMetricOmmPoolFactoryActions(pool).setPause(0);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L643-645)
```text
  function _checkNotPaused() internal view {
    if (pauseLevel != 0) revert PoolPaused();
  }
```
