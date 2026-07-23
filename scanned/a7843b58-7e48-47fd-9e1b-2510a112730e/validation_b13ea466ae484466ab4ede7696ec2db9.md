### Title
`protocolUnpausePool` Assigns Wrong Pause Level (1 Instead of 0), Leaving Pool Permanently Swap-Paused After Protocol Unpause - (File: metric-core/contracts/MetricOmmPoolFactory.sol)

---

### Summary

`MetricOmmPoolFactory.protocolUnpausePool` is designed to let the protocol owner restore a protocol-paused pool (level 2) to active state. However, it sets the pause level to **1** (admin-paused) instead of **0** (active). Because `_checkNotPaused` rejects any non-zero pause level, swaps remain blocked after the protocol owner "unpauses" the pool. The pool admin must then separately call `unpausePool` to reach level 0. If the admin is unavailable, the pool is permanently stuck in a paused state.

---

### Finding Description

The three pause levels are:

| Level | Meaning |
|---|---|
| 0 | Active (swaps allowed) |
| 1 | Paused by admin |
| 2 | Paused by protocol |

`_checkNotPaused` blocks swaps for **any** non-zero level: [1](#0-0) 

`protocolUnpausePool` transitions from level 2 → **1**, not 2 → 0: [2](#0-1) 

The wrong target value `1` is also embedded in the revert message `InvalidPauseTransition(cur, 1)`, confirming the assignment is consistently wrong throughout the function. By contrast, `unpausePool` (admin-only) correctly transitions 1 → 0: [3](#0-2) 

The admin-only `unpausePool` enforces `cur != 1` as its precondition, so it can only be called from level 1. After `protocolUnpausePool` sets the pool to level 1, the admin must cooperate to reach level 0. The protocol owner has no path to set level 0 directly.

---

### Impact Explanation

After the protocol owner calls `protocolUnpausePool` on a level-2 pool, the pool is left at level 1. All swap calls revert with `PoolPaused`. `addLiquidity` and `removeLiquidity` are unaffected (no `whenNotPaused` guard), so LP principal is not directly lost, but the core swap functionality — the primary revenue-generating operation — is completely unusable. If the pool admin key is lost or the admin is uncooperative, the pool is permanently stuck in a paused state with no recovery path available to the protocol owner.

---

### Likelihood Explanation

The trigger requires the protocol owner to call `protocolUnpausePool` (a normal operational action after an emergency pause is resolved). The wrong value is always written — there is no conditional path that produces the correct level 0. The scenario where the admin is unavailable to follow up is realistic in practice (key loss, multisig quorum failure, etc.).

---

### Recommendation

Change the target pause level in `protocolUnpausePool` from `1` to `0`:

```solidity
function protocolUnpausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
-   if (cur != 2) revert InvalidPauseTransition(cur, 1);
-   IMetricOmmPoolFactoryActions(pool).setPause(1);
+   if (cur != 2) revert InvalidPauseTransition(cur, 0);
+   IMetricOmmPoolFactoryActions(pool).setPause(0);
}
```

---

### Proof of Concept

1. Pool is active (level 0).
2. Protocol owner calls `protocolPausePool` → pool moves to level 2. Swaps revert.
3. Emergency resolved. Protocol owner calls `protocolUnpausePool`.
4. Pool is set to level 1 (admin-paused). Swaps **still revert** with `PoolPaused`.
5. Protocol owner has no further recourse — `protocolUnpausePool` requires `cur == 2` to proceed, and `unpausePool` is `onlyPoolAdmin`.
6. If the pool admin is unavailable, the pool is permanently swap-paused despite the protocol owner having "unpaused" it. [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L643-645)
```text
  function _checkNotPaused() internal view {
    if (pauseLevel != 0) revert PoolPaused();
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L392-403)
```text
  function protocolPausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 0 && cur != 1) revert InvalidPauseTransition(cur, 2);
    IMetricOmmPoolFactoryActions(pool).setPause(2);
  }

  /// @inheritdoc IMetricOmmPoolFactoryOwner
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
