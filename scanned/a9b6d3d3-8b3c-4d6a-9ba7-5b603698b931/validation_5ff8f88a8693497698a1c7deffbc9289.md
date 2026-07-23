### Title
`protocolUnpausePool` Sets Pause Level to 1 (Admin-Paused) Instead of 0 (Active), Leaving Pool Permanently Paused After Protocol Unpause — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.protocolUnpausePool` is intended to restore a protocol-paused pool (level 2) to active status, but it calls `setPause(1)` instead of `setPause(0)`. After the protocol owner calls `protocolUnpausePool`, the pool transitions from level 2 (protocol-paused) to level 1 (admin-paused) — still paused. Swaps remain blocked. The protocol owner has no path to directly restore swap functionality; the pool admin must separately call `unpausePool` to complete the transition to level 0.

---

### Finding Description

The pool defines three pause levels:

```
0 = active
1 = paused by admin
2 = paused by protocol
``` [1](#0-0) 

`_checkNotPaused()` reverts on any non-zero level: [2](#0-1) 

`protocolUnpausePool` reads the current level, asserts it is 2, then calls `setPause(1)`: [3](#0-2) 

Level 1 still satisfies `pauseLevel != 0`, so `swap` continues to revert with `PoolPaused` after the "unpause" call.

The admin-side `unpausePool` enforces `cur == 1 → 0`: [4](#0-3) 

So the only path to level 0 after a protocol pause is: protocol calls `protocolUnpausePool` (→ level 1), then the pool admin separately calls `unpausePool` (→ level 0). The protocol owner alone cannot restore the pool to active.

---

### Impact Explanation

After `protocolUnpausePool` is called, `swap` still reverts with `PoolPaused` because `pauseLevel == 1 != 0`. Core pool swap functionality remains broken. If the pool was at level 0 (active) before the protocol pause, the admin never issued a pause and may not know they must call `unpausePool`. If the admin is unresponsive, the pool is permanently stuck at level 1. LPs can still call `removeLiquidity` (no `whenNotPaused` guard there), but all swap volume and fee accrual is lost until the admin acts. [5](#0-4) 

---

### Likelihood Explanation

Any time the protocol owner exercises `protocolUnpausePool` — a routine governance action — the bug fires unconditionally. No special preconditions, no attacker required. Every protocol-pause/unpause cycle leaves the pool admin-paused.

---

### Recommendation

Change `setPause(1)` to `setPause(0)` in `protocolUnpausePool`:

```solidity
function protocolUnpausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 2) revert InvalidPauseTransition(cur, 0);
-   IMetricOmmPoolFactoryActions(pool).setPause(1);
+   IMetricOmmPoolFactoryActions(pool).setPause(0);
}
``` [3](#0-2) 

---

### Proof of Concept

1. Pool is active: `pauseLevel == 0`.
2. Protocol owner calls `protocolPausePool(pool)` → `setPause(2)` → `pauseLevel == 2`. Swaps revert.
3. Protocol owner calls `protocolUnpausePool(pool)`:
   - Reads `cur == 2` ✓ passes the guard.
   - Calls `setPause(1)` → `pauseLevel == 1`.
4. Any user calls `swap(...)` → `_checkNotPaused()` → `pauseLevel != 0` → **`PoolPaused` revert**.
5. Pool admin must separately call `unpausePool(pool)` (checks `cur == 1`) → `setPause(0)` to restore swaps.
6. If admin is absent or unresponsive, the pool remains permanently paused at level 1 despite the protocol owner having "unpaused" it. [6](#0-5) [7](#0-6)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L71-72)
```text
  /// @dev 0 = active, 1 = paused by admin, 2 = paused by protocol. Transitions enforced by factory.
  uint8 internal pauseLevel;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L174-177)
```text
  modifier whenNotPaused() {
    _checkNotPaused();
    _;
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L217-224)
```text
  function swap(
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
```

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
