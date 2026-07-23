The code is confirmed. The vulnerability is real:

- `purgeStateGuardRole` (L120-124) only deletes `stateGuard[feedId]`, not `pendingStateGuard[feedId]`
- `acceptStateGuardRole` (L111-118) has no access control beyond `pendingStateGuard[feedId] == msg.sender`
- `purgePendingStateGuardRole` (L105-109) exists but requires `checkRole`, which after purge falls back to ADMIN_ROLE — creating a race window
- The stale `pendingStateGuard` allows B to call `acceptStateGuardRole` and become `stateGuard` without ADMIN consent, then call `setPriceGuard` to disable price bounds

---

Audit Report

## Title
Stale `pendingStateGuard` Not Cleared in `purgeStateGuardRole` Allows Unauthorized Oracle Role Takeover — (File: `smart-contracts-poc/contracts/oracles/providers/OracleBase.sol`)

## Summary
`purgeStateGuardRole` deletes `stateGuard[feedId]` but leaves `pendingStateGuard[feedId]` intact. A previously nominated address can call the permissionless `acceptStateGuardRole` after the guard has purged itself, gaining unauthorized `stateGuard` control. The unauthorized guard can then call `setPriceGuard` to disable price bounds, allowing stale or manipulated prices to reach Metric OMM pool swaps.

## Finding Description
`OracleBase` implements a two-step guard-transfer pattern. `setStateGuardRole` writes `pendingStateGuard[feedId]` and `acceptStateGuardRole` promotes the pending address to `stateGuard`. The `purgeStateGuardRole` function is intended to remove the current guard entirely:

```solidity
// L120-124
function purgeStateGuardRole(bytes32 feedId) external checkRole(feedId) {
    delete stateGuard[feedId];
    emit StateGuardDeleted(feedId);
}
``` [1](#0-0) 

It does not delete `pendingStateGuard[feedId]`. `acceptStateGuardRole` has no access control beyond the pending check:

```solidity
// L111-118
function acceptStateGuardRole(bytes32 feedId) external {
    require(pendingStateGuard[feedId] == msg.sender, InvalidGuard(msg.sender));
    delete pendingStateGuard[feedId];
    stateGuard[feedId] = msg.sender;
    emit StateGuardUpdated(feedId, msg.sender);
}
``` [2](#0-1) 

After `purgeStateGuardRole`, `checkRole` falls back to `ADMIN_ROLE` since `stateGuard[feedId]` is zero: [3](#0-2) 

The mitigation path — `purgePendingStateGuardRole` — now requires ADMIN to act, but B can front-run this call and call `acceptStateGuardRole` first, installing itself as `stateGuard` without ADMIN consent. [4](#0-3) 

## Impact Explanation
The unauthorized `stateGuard` can call `setPriceGuard(feedId, 1, type(uint128).max)`, effectively disabling price bounds for the feed: [5](#0-4) 

With bounds disabled, any price — stale, inverted, or manipulated — passes the guard and is consumed by Metric OMM pools via the `price(feedId, pool)` path, constituting bad-price execution and an admin-boundary break (oracle role checks bypassed by an unprivileged path). This can cause swap conservation failure or direct loss of trader principal.

## Likelihood Explanation
The trigger sequence is realistic and requires no special privileges beyond having been nominated as a pending guard at any prior point. The race between B calling `acceptStateGuardRole` and ADMIN calling `purgePendingStateGuardRole` is non-atomic and not guaranteed to be won by ADMIN, especially if the nomination was not publicly announced. The guard calling `purgeStateGuardRole` would naturally believe this cancels all pending nominations, making the missing `delete` a likely operational mistake.

## Recommendation
In `purgeStateGuardRole`, also delete `pendingStateGuard[feedId]`:

```diff
function purgeStateGuardRole(bytes32 feedId) external checkRole(feedId) {
    delete stateGuard[feedId];
+   delete pendingStateGuard[feedId];
    emit StateGuardDeleted(feedId);
}
```

This ensures removing the active guard atomically cancels any in-flight nomination, mirroring the behavior of `acceptStateGuardRole` which correctly clears both mappings.

## Proof of Concept
```solidity
// 1. Guard A nominates B
oracle.setStateGuardRole(feedId, address(B));
assertEq(oracle.pendingStateGuard(feedId), address(B));

// 2. Guard A purges itself (intending to cancel the nomination)
oracle.purgeStateGuardRole(feedId);
assertEq(oracle.stateGuard(feedId), address(0));
// pendingStateGuard is NOT cleared:
assertEq(oracle.pendingStateGuard(feedId), address(B)); // still set

// 3. B accepts — no ADMIN consent required
vm.prank(address(B));
oracle.acceptStateGuardRole(feedId);
assertEq(oracle.stateGuard(feedId), address(B)); // B is now guard

// 4. B disables the price guard
vm.prank(address(B));
oracle.setPriceGuard(feedId, 1, type(uint128).max);
// Any price, including stale/manipulated, now passes the guard
// and will be consumed by Metric OMM pools on the next swap
```

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

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L88-97)
```text
    function setPriceGuard(bytes32 feedId, uint128 minPrice, uint128 maxPrice)
        external
        checkRole(feedId)
    {
        require(minPrice < maxPrice);

        priceGuard[feedId] = PriceGuard({min: minPrice, max: maxPrice});

        emit PriceGuardUpdated(feedId, minPrice, maxPrice);
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
