### Title
`PAUSER_ROLE` Never Assigned During Initialization Leaves All L2 Pools Permanently Unpausable at Deployment - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
Every L2 pool contract in the LRT-rsETH protocol defines a `PAUSER_ROLE` and exposes a `pause()` function gated by that role, but **no address is ever granted `PAUSER_ROLE` during initialization**. The pool is therefore structurally unpausable from the moment of deployment until the admin separately calls `grantRole(PAUSER_ROLE, ...)`. This is the direct analog of the referenced report's finding that the system can remain without a critical operational role.

### Finding Description
In `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPool.sol`, and `RSETHPoolNoWrapper.sol`, the `initialize()` function grants `DEFAULT_ADMIN_ROLE` and `BRIDGER_ROLE` but never grants `PAUSER_ROLE`.

`RSETHPoolV3.initialize()` grants only two roles: [1](#0-0) 

`RSETHPoolV3ExternalBridge.initialize()` similarly grants only two roles: [2](#0-1) 

`RSETHPoolNoWrapper.initialize()` grants only two roles: [3](#0-2) 

Yet `pause()` in every pool is gated exclusively by `PAUSER_ROLE`: [4](#0-3) [5](#0-4) [6](#0-5) 

None of the reinitializers in any pool contract ever grant `PAUSER_ROLE` either. The role is declared: [7](#0-6) 

but has zero holders from deployment until the admin takes an explicit out-of-band action.

The underlying `AccessControlUpgradeable` does not protect against this: it simply stores role membership in a mapping and has no invariant requiring at least one holder of any given role. [8](#0-7) 

### Impact Explanation
**Medium — Temporary freezing of funds.**

The pools hold user-deposited ETH and LSTs (e.g., wstETH) that are batched and bridged to L1. The `pause()` mechanism is the protocol's only on-chain emergency stop for deposits. If an exploit, oracle manipulation, or bridge failure occurs in the window between deployment and the admin's manual `grantRole(PAUSER_ROLE, ...)` call, no address can call `pause()`. Deposits continue flowing into the compromised pool, and the bridger can continue moving those assets to L1, with no on-chain mechanism to halt the flow. User funds deposited during this window are at risk of being lost or frozen in a broken state.

### Likelihood Explanation
The gap exists from block 0 of deployment and persists until the admin takes a separate transaction. Given that multiple pool variants across multiple chains all share this omission, it is a systematic pattern rather than a one-off oversight. Any emergency in the deployment-to-role-grant window — including a front-run exploit on a newly deployed pool — triggers the impact with no recourse.

### Recommendation
Grant `PAUSER_ROLE` to the `admin` address inside every `initialize()` function, mirroring the pattern already used for `BRIDGER_ROLE`:

```solidity
_grantRole(DEFAULT_ADMIN_ROLE, admin);
_grantRole(BRIDGER_ROLE, bridger);
_grantRole(PAUSER_ROLE, admin); // add this
```

Alternatively, enforce a post-deployment invariant check that reverts if `PAUSER_ROLE` has zero members.

### Proof of Concept

1. Deploy `RSETHPoolV3` with any `admin` and `bridger` addresses.
2. Immediately after deployment, call `hasRole(PAUSER_ROLE, admin)` → returns `false`.
3. Call `hasRole(PAUSER_ROLE, bridger)` → returns `false`.
4. Attempt `pool.pause()` from any address → reverts with `AccessControl: account ... is missing role ...`.
5. An attacker exploits a bug in the pool; the protocol team cannot halt deposits on-chain.
6. Only after the admin submits a separate `grantRole(PAUSER_ROLE, pauser)` transaction does `pause()` become callable — but the damage window has already been open since deployment.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L63-63)
```text
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
```

**File:** contracts/pools/RSETHPoolV3.sol (L225-226)
```text
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/pools/RSETHPoolV3.sol (L592-595)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L345-347)
```text
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L860-863)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L210-211)
```text
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(BRIDGER_ROLE, manager);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L673-675)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        _pause();
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/AccessControlUpgradeable.sol (L57-62)
```text
    struct RoleData {
        mapping(address => bool) members;
        bytes32 adminRole;
    }

    mapping(bytes32 => RoleData) private _roles;
```
