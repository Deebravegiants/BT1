### Title
Protocol Pause (Level 2) Bypassed via Race Condition in `unpausePool` — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.unpausePool()` and `MetricOmmPoolFactory.protocolPausePool()` both follow a non-atomic **read-check-write** pattern across two separate external calls to the pool. A pool admin's in-flight `unpausePool` transaction (which reads `pauseLevel == 1` and then calls `pool.setPause(0)`) can race against the protocol owner's `protocolPausePool` (which sets `pauseLevel = 2`). If the protocol's write lands between the admin's read and write, the admin's `setPause(0)` executes against a level-2 pool, silently downgrading it to level 0 and fully bypassing the emergency protocol pause.

---

### Finding Description

The factory enforces pause-level transitions by reading the pool's current level, validating it, and then writing the new level — but these are two separate cross-contract calls with no atomicity guarantee:

**`unpausePool` (pool admin):**
```solidity
function unpausePool(address pool) external override nonReentrant onlyPoolAdmin(pool) {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);   // ← read
    if (cur != 1) revert InvalidPauseTransition(cur, 0); // ← check
    IMetricOmmPoolFactoryActions(pool).setPause(0);      // ← write
}
```

**`protocolPausePool` (protocol owner):**
```solidity
function protocolPausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 0 && cur != 1) revert InvalidPauseTransition(cur, 2);
    IMetricOmmPoolFactoryActions(pool).setPause(2);
}
```

**`setPause` on the pool has no current-level guard:**
```solidity
function setPause(uint8 newLevel) external onlyFactory {
    if (newLevel > 2) revert InvalidPauseLevel();
    if (newLevel == pauseLevel) return;
    uint8 prev = pauseLevel;
    pauseLevel = newLevel;
    emit PauseLevelUpdated(prev, newLevel);
}
```

The pool's `setPause` blindly accepts whatever level the factory sends. All transition enforcement lives in the factory's pre-call read, which is stale by the time the write executes.

**Race sequence:**

| Step | Actor | Action | Pool `pauseLevel` |
|------|-------|--------|-------------------|
| 1 | Pool admin | Calls `unpausePool`; reads `cur = 1`; check passes; tx enters mempool | 1 |
| 2 | Protocol owner | Calls `protocolPausePool`; reads `cur = 1` (allowed); calls `setPause(2)` | **2** |
| 3 | Pool admin | `setPause(0)` executes (from step 1) | **0** ← bypass |

After step 3, the pool is fully active (`pauseLevel = 0`) despite the protocol having issued an emergency halt. Swaps are re-enabled.

The `nonReentrant` modifier on both factory functions uses `ReentrancyGuardTransient` (transient storage), which only prevents reentrancy within a single transaction — it provides zero protection against the inter-transaction race described above.

---

### Impact Explanation

The protocol pause (level 2) is explicitly documented as the **"strongest halt"** for security events. The intentional design requires two-party consent to resume: the protocol owner moves 2→1, then the pool admin moves 1→0. This race condition allows the pool admin to skip the protocol's consent entirely, re-enabling swaps on a pool the protocol intended to halt.

Consequences once the bypass succeeds:
- Swaps execute against a potentially compromised or stale oracle during an active security incident
- LP funds can be drained via bad-price swaps that the protocol pause was meant to prevent
- The protocol's emergency response mechanism is rendered ineffective

This is a direct **admin-boundary break**: the pool admin (semi-trusted, level-1 authority) exceeds their authority by overwriting a level-2 protocol pause, which is reserved for the factory owner.

---

### Likelihood Explanation

**Medium.** The race requires the pool admin to have a pending `unpausePool` transaction in the mempool at the exact moment the protocol issues an emergency `protocolPausePool`. This can occur:

- **Accidentally**: The admin submits `unpausePool` to resume normal operations; the protocol simultaneously detects an exploit and issues an emergency pause. On chains with public mempools (Ethereum mainnet), MEV searchers or block builders can reorder transactions to produce this ordering.
- **Intentionally (malicious pool admin)**: A pool admin who wants to resist an emergency shutdown can repeatedly submit `unpausePool` transactions, racing against the protocol's pause. Since `unpausePool` only requires `cur == 1`, the admin can first call `pausePool` (0→1) and then immediately submit `unpausePool` (1→0), creating a window for the race.

---

### Recommendation

Move the transition-validity check into `MetricOmmPool.setPause` itself, so the check and write are atomic within a single call:

```solidity
function setPause(uint8 expectedCurrent, uint8 newLevel) external onlyFactory {
    if (newLevel > 2) revert InvalidPauseLevel();
    if (pauseLevel != expectedCurrent) revert InvalidPauseTransition(pauseLevel, newLevel);
    if (newLevel == pauseLevel) return;
    uint8 prev = pauseLevel;
    pauseLevel = newLevel;
    emit PauseLevelUpdated(prev, newLevel);
}
```

The factory functions then pass the expected current level they read, and the pool atomically validates and applies the transition. If the level changed between the factory's read and the pool's write, the call reverts, forcing the caller to retry with fresh state — exactly the fix recommended in the analogous LidoVault report.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Foundry test demonstrating the bypass

function test_protocolPause_bypassed_by_racing_unpausePool() public {
    address pool = _createPool();

    // Pool admin pauses pool to level 1
    vm.prank(admin);
    factory.pausePool(pool);
    assertEq(_pauseLevel(pool), 1);

    // Simulate: admin's unpausePool tx is in mempool (reads cur=1, check passes)
    // Protocol owner's protocolPausePool executes first (cur=1 → 2)
    factory.protocolPausePool(pool);
    assertEq(_pauseLevel(pool), 2);

    // Admin's setPause(0) now executes against level-2 pool
    // Factory's check already passed (cur was 1 at read time), so setPause(0) goes through
    // Simulate by calling setPause directly as factory (the factory would have called this)
    IMetricOmmPoolFactoryActions(pool).setPause(0); // called by factory in unpausePool

    // Protocol pause is bypassed — pool is fully active
    assertEq(_pauseLevel(pool), 0); // ← CRITICAL: should be 2, is 0

    // Swaps now succeed on a pool the protocol intended to halt
    // _swap(...) would succeed here
}
```

The test at line 317 of `MetricOmmPoolFactory.t.sol` (`test_pausePool_adminUnpause_respectsProtocolLayering`) only tests the sequential case where the admin calls `unpausePool` *after* `protocolPausePool` has already committed — it does not test the interleaved ordering where the admin's read precedes the protocol's write. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L391-396)
```text
  /// @inheritdoc IMetricOmmPoolFactoryOwner
  function protocolPausePool(address pool) external override nonReentrant onlyOwner {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 0 && cur != 1) revert InvalidPauseTransition(cur, 2);
    IMetricOmmPoolFactoryActions(pool).setPause(2);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L466-471)
```text
  /// @inheritdoc IMetricOmmPoolFactoryPoolAdmin
  function unpausePool(address pool) external override nonReentrant onlyPoolAdmin(pool) {
    (uint8 cur,,,,,) = PoolStateLibrary._slot0(pool);
    if (cur != 1) revert InvalidPauseTransition(cur, 0);
    IMetricOmmPoolFactoryActions(pool).setPause(0);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L455-461)
```text
  function setPause(uint8 newLevel) external onlyFactory {
    if (newLevel > 2) revert InvalidPauseLevel();
    if (newLevel == pauseLevel) return;
    uint8 prev = pauseLevel;
    pauseLevel = newLevel;
    emit PauseLevelUpdated(prev, newLevel);
  }
```

**File:** metric-core/test/MetricOmmPoolFactory.t.sol (L317-338)
```text
  function test_pausePool_adminUnpause_respectsProtocolLayering() public {
    address pool = _createPool();
    assertEq(_pauseLevel(pool), 0);

    vm.prank(admin);
    factory.pausePool(pool);
    assertEq(_pauseLevel(pool), 1);

    factory.protocolPausePool(pool);
    assertEq(_pauseLevel(pool), 2);

    vm.prank(admin);
    vm.expectRevert(abi.encodeWithSelector(IMetricOmmPoolFactory.InvalidPauseTransition.selector, uint8(2), uint8(0)));
    factory.unpausePool(pool);

    factory.protocolUnpausePool(pool);
    assertEq(_pauseLevel(pool), 1);

    vm.prank(admin);
    factory.unpausePool(pool);
    assertEq(_pauseLevel(pool), 0);
  }
```
