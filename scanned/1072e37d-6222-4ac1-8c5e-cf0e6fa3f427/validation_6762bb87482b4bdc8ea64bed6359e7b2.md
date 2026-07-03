### Title
`TIME_LOCK_ROLE` Guard on `addNewSupportedAsset` Provides No Actual Timelock Enforcement - (File: contracts/LRTConfig.sol)

### Summary
`LRTConfig.sol` guards `addNewSupportedAsset()` with `onlyRole(LRTConstants.TIME_LOCK_ROLE)`, a role whose name explicitly implies a timelock contract must hold it. However, no timelock contract is deployed, referenced, or enforced anywhere in the codebase. The `DEFAULT_ADMIN_ROLE` holder can grant `TIME_LOCK_ROLE` to any EOA, making the stated timelock protection entirely illusory — exactly the same class of bug as the reference report where `_setupDelayForRenouncingOwnership` was never called, leaving `delay = 0`.

### Finding Description
`LRTConstants.sol` defines `TIME_LOCK_ROLE = keccak256("TIME_LOCK_ROLE")` as a named role constant. [1](#0-0) 

`LRTConfig.sol` uses this role as the sole access guard on `addNewSupportedAsset()`:

```solidity
function addNewSupportedAsset(address asset, uint256 depositLimit)
    external
    onlyRole(LRTConstants.TIME_LOCK_ROLE)
{
    _addNewSupportedAsset(asset, depositLimit);
}
``` [2](#0-1) 

The role name `TIME_LOCK_ROLE` communicates a design intent: the holder of this role should be a `TimelockController` contract that enforces a mandatory delay before execution. This is the standard pattern for protecting critical protocol configuration changes (adding new deposit assets) so that users have time to review and exit before the change takes effect.

However:
1. The `initialize()` function in `LRTConfig.sol` never grants `TIME_LOCK_ROLE` to any address. [3](#0-2) 
2. No `TimelockController` contract exists anywhere in the production `contracts/` directory.
3. `AccessControlUpgradeable` (which `LRTConfig` inherits) allows the `DEFAULT_ADMIN_ROLE` holder to grant `TIME_LOCK_ROLE` to any EOA via `grantRole()` — no delay is enforced by the role mechanism itself.

The result is structurally identical to the reference bug: a timelock is named and implied by the code structure, but the actual delay enforcement is never implemented. Any address granted `TIME_LOCK_ROLE` — including a plain EOA — can call `addNewSupportedAsset()` immediately with no delay.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The `TIME_LOCK_ROLE` guard communicates to auditors, integrators, and users that adding new supported assets is subject to a timelock delay, giving users time to review and exit. In practice, no such delay exists. A new asset (e.g., a rebasing token with unusual accounting, or a token with a fee-on-transfer) can be added to the protocol instantly by whoever holds `TIME_LOCK_ROLE`, with no on-chain delay enforcing a review window. The protocol fails to deliver the timelock protection it structurally implies.

### Likelihood Explanation
The likelihood of the missing enforcement being exploited depends on who is granted `TIME_LOCK_ROLE`. Since the role is never assigned in `initialize()`, the admin must explicitly grant it. If granted to an EOA (the path of least resistance for operational convenience), the timelock protection is absent from day one of live operation. This is a realistic deployment outcome.

### Recommendation
Enforce the timelock at the contract level. Deploy an OpenZeppelin `TimelockController` with a meaningful minimum delay (e.g., 24–48 hours), grant it `TIME_LOCK_ROLE` in the deployment script, and document this in the `initialize()` NatSpec. Optionally, add a check in `LRTConfig` that validates the `TIME_LOCK_ROLE` holder has a minimum delay:

```solidity
// In addNewSupportedAsset, verify caller is a TimelockController with sufficient delay
require(
    ITimelockController(msg.sender).getMinDelay() >= MIN_TIMELOCK_DELAY,
    "Timelock delay insufficient"
);
```

At minimum, the deployment must assign `TIME_LOCK_ROLE` to a real `TimelockController`, not an EOA.

### Proof of Concept
1. `LRTConfig` is deployed and initialized. `TIME_LOCK_ROLE` is held by no one.
2. Admin calls `grantRole(TIME_LOCK_ROLE, adminEOA)` — a single transaction, no delay.
3. `adminEOA` immediately calls `addNewSupportedAsset(maliciousToken, depositLimit)`.
4. `maliciousToken` is now a supported deposit asset with no on-chain delay having elapsed.
5. Users who monitor the protocol for new asset additions have zero blocks of advance notice enforced by the contract — the "timelock" named in the role constant provided no protection. [2](#0-1) [1](#0-0)

### Citations

**File:** contracts/utils/LRTConstants.sol (L39-39)
```text
    bytes32 public constant TIME_LOCK_ROLE = keccak256("TIME_LOCK_ROLE");
```

**File:** contracts/LRTConfig.sol (L49-62)
```text
    function initialize(address admin, address stETH, address ethX, address rsETH_) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(rsETH_);

        __AccessControl_init();
        _setToken(LRTConstants.ST_ETH_TOKEN, stETH);
        _setToken(LRTConstants.ETHX_TOKEN, ethX);
        _addNewSupportedAsset(stETH, 100_000 ether);
        _addNewSupportedAsset(ethX, 100_000 ether);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);

        rsETH = rsETH_;
    }
```

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```
