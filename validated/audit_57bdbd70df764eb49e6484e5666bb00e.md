### Title
`purgeStateGuardRole` Does Not Clear `pendingStateGuard`, Allowing a Pending Guard to Seize the Oracle Role After the Current Guard Abdicates — (File: smart-contracts-poc/contracts/oracles/providers/OracleBase.sol)

---

### Summary

`purgeStateGuardRole` deletes `stateGuard[feedId]` but leaves `pendingStateGuard[feedId]` intact. A pending guard that was nominated before the abdication can still call `acceptStateGuardRole` and become the new `stateGuard`, gaining unauthorized control over `setPriceGuard` for that feed — the exact structural analog of the `_abdicate()` / `pendingGov` bug in the seed report.

---

### Finding Description

In `smart-contracts-poc/contracts/oracles/providers/OracleBase.sol`, the two-step guard-transfer flow is:

```
setStateGuardRole(feedId, newGuard)   → pendingStateGuard[feedId] = newGuard
acceptStateGuardRole(feedId)          → stateGuard[feedId] = msg.sender; delete pendingStateGuard
```

The abdication path is:

```solidity
// OracleBase.sol L120-124
function purgeStateGuardRole(bytes32 feedId) external checkRole(feedId) {
    delete stateGuard[feedId];          // ← clears active guard
    // pendingStateGuard[feedId] is NOT cleared
    emit StateGuardDeleted(feedId);
}
```

`acceptStateGuardRole` has no dependency on `stateGuard`; it only checks `pendingStateGuard`:

```solidity
// OracleBase.sol L111-118
function acceptStateGuardRole(bytes32 feedId) external {
    require(pendingStateGuard[feedId] == msg.sender, InvalidGuard(msg.sender));
    delete pendingStateGuard[feedId];
    stateGuard[feedId] = msg.sender;
    emit StateGuardUpdated(feedId, msg.sender);
}
```

After `purgeStateGuardRole` executes, `stateGuard[feedId]` is `address(0)` and `checkRole` falls back to `ADMIN_ROLE`. However, the pending nominee can immediately call `acceptStateGuardRole` and install themselves as the new `stateGuard` — overriding the ADMIN's restored authority — before ADMIN can call `purgePendingStateGuardRole`.

A separate `purgePendingStateGuardRole` function exists, confirming the protocol intended pending state to be clearable, but `purgeStateGuardRole` never invokes it.

---

### Impact Explanation

`stateGuard` is the sole authority for `setPriceGuard` on a feed once set (ADMIN is locked out):

```solidity
// OracleBase.sol L65-74
modifier checkRole(bytes32 feedId) {
    address _guard = stateGuard[feedId];
    if (_guard != address(0)) {
        require(_guard == msg.sender, InvalidGuard(msg.sender));
    } else {
        _checkRole(ADMIN_ROLE);
    }
    _;
}
```

An attacker who seizes `stateGuard` can call `setPriceGuard(feedId, 1, type(uint128).max)`, effectively disabling the price band. The test suite confirms guards are enforced at the price-provider layer (not the oracle), meaning a disabled guard allows any oracle price — including stale or manipulated values — to flow into `MetricOmmPool` swap execution. This satisfies the allowed impact gate: **bad-price execution** (unbounded bid/ask quote reaches a pool swap) and **oracle role check bypassed by an unprivileged path**.

---

### Likelihood Explanation

The trigger requires two sequential actions by the current guard:

1. `setStateGuardRole(feedId, attacker)` — nominating a pending guard (possibly a legitimate earlier proposal that was later reconsidered).
2. `purgeStateGuardRole(feedId)` — intending to fully abdicate and return control to ADMIN.

This is a realistic operational sequence (guard decides to step down after having proposed a successor). The attacker can also front-run any ADMIN `purgePendingStateGuardRole` call in the same block as the abdication, making the window exploitable even if ADMIN reacts quickly.

---

### Recommendation

Clear `pendingStateGuard` inside `purgeStateGuardRole`:

```solidity
function purgeStateGuardRole(bytes32 feedId) external checkRole(feedId) {
    delete stateGuard[feedId];
+   delete pendingStateGuard[feedId];   // prevent stale nominee from claiming
    emit StateGuardDeleted(feedId);
}
```

---

### Proof of Concept

```
1. ADMIN calls setStateGuardRole(feedId, guard1)
2. guard1 calls acceptStateGuardRole(feedId)
   → stateGuard[feedId] = guard1

3. guard1 calls setStateGuardRole(feedId, attacker)
   → pendingStateGuard[feedId] = attacker

4. guard1 decides to abdicate:
   guard1 calls purgeStateGuardRole(feedId)
   → stateGuard[feedId] = address(0)
   → pendingStateGuard[feedId] = attacker  ← NOT cleared

5. attacker calls acceptStateGuardRole(feedId)
   → pendingStateGuard[feedId] == attacker ✓
   → stateGuard[feedId] = attacker         ← unauthorized seizure

6. attacker calls setPriceGuard(feedId, 1, type(uint128).max)
   → price guard disabled; any oracle price accepted by price provider
   → pool swaps execute at unbounded prices
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L65-74)
```text
    modifier checkRole(bytes32 feedId) {
        address _guard = stateGuard[feedId];
        if (_guard != address(0)) {
            require(_guard == msg.sender, InvalidGuard(msg.sender));
        } else {
            _checkRole(ADMIN_ROLE);
        }

        _;
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L99-103)
```text
    function setStateGuardRole(bytes32 feedId, address newGuard) external checkRole(feedId) {
        pendingStateGuard[feedId] = newGuard;

        emit StateGuardPending(feedId, newGuard);
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L105-109)
```text
    function purgePendingStateGuardRole(bytes32 feedId) external checkRole(feedId) {
        delete pendingStateGuard[feedId];

        emit PendingStateGuardDeleted(feedId);
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L111-118)
```text
    function acceptStateGuardRole(bytes32 feedId) external {
        require(pendingStateGuard[feedId] == msg.sender, InvalidGuard(msg.sender));

        delete pendingStateGuard[feedId];
        stateGuard[feedId] = msg.sender;

        emit StateGuardUpdated(feedId, msg.sender);
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L120-124)
```text
    function purgeStateGuardRole(bytes32 feedId) external checkRole(feedId) {
        delete stateGuard[feedId];

        emit StateGuardDeleted(feedId);
    }
```
