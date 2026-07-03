### Title
Missing Zero-Address Check on `admin` in `RSETHPoolV2.initialize` Permanently Freezes Admin Control - (File: contracts/pools/RSETHPoolV2.sol)

---

### Summary

`RSETHPoolV2.initialize` grants `DEFAULT_ADMIN_ROLE` and `BRIDGER_ROLE` to the `admin` parameter without validating it against `address(0)`. If `address(0)` is passed as `admin`, all admin-gated functions become permanently inaccessible, including the `reinitialize` upgrade path and all role-management operations.

---

### Finding Description

`RSETHPoolV2.initialize` performs `UtilLib.checkNonZeroAddress` on `_wrsETH` and `_rsETHOracle`, but omits the same check for `admin` and `bridger`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
    UtilLib.checkNonZeroAddress(_wrsETH);       // checked
    UtilLib.checkNonZeroAddress(_rsETHOracle);  // checked
    // admin and bridger are NOT checked
    __ERC20_init("rsETH", "rsETH");
    __AccessControl_init();
    __ReentrancyGuard_init();
    _grantRole(DEFAULT_ADMIN_ROLE, admin);      // admin may be address(0)
    _setupRole(BRIDGER_ROLE, admin);
    _setupRole(BRIDGER_ROLE, bridger);
    ...
}
``` [1](#0-0) 

If `admin == address(0)` is supplied, `DEFAULT_ADMIN_ROLE` is permanently assigned to `address(0)`. OpenZeppelin's `AccessControlUpgradeable` uses `hasRole(DEFAULT_ADMIN_ROLE, msg.sender)` for all admin checks; since no EOA or contract controls `address(0)`, every admin-gated function becomes permanently uncallable.

The `reinitialize` function, which is the only upgrade path for bridge parameters (`_l2Bridge`, `_l1VaultETHForL2Chain`, `_messenger`), is gated by `onlyRole(DEFAULT_ADMIN_ROLE)`:

```solidity
function reinitialize(
    address _l2Bridge,
    address _l1VaultETHForL2Chain,
    address _messenger
) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
``` [2](#0-1) 

This means the pool is permanently locked into its initial bridge configuration with no recovery path.

---

### Impact Explanation

**Medium — Temporary (effectively permanent) freezing of funds and contract fails to deliver promised returns.**

With `DEFAULT_ADMIN_ROLE` assigned to `address(0)`:
- No one can call `reinitialize` to update bridge addresses.
- No one can grant or revoke any role (role management requires `DEFAULT_ADMIN_ROLE`).
- No one can pause the contract in an emergency (if the pauser role needs to be re-granted).
- ETH deposited by users into the pool cannot be bridged to L1 if the bridge address becomes stale or invalid, effectively freezing user funds in the pool.

---

### Likelihood Explanation

**Low.** This requires a deployment error where `address(0)` is passed as `admin`. While not attacker-triggered in the traditional sense, the absence of a guard makes it a latent risk during deployment or proxy re-initialization. The analogous pattern (missing zero-address check on admin setter) was classified as Medium Risk in the reference report precisely because it is a realistic operational mistake.

---

### Recommendation

Add `UtilLib.checkNonZeroAddress(admin)` and `UtilLib.checkNonZeroAddress(bridger)` at the top of `RSETHPoolV2.initialize`, consistent with how other contracts in the codebase (e.g., `LRTConfig.initialize`, `TokenSwap.initialize`) guard their admin parameters:

```solidity
function initialize(...) external initializer {
    UtilLib.checkNonZeroAddress(admin);      // add this
    UtilLib.checkNonZeroAddress(bridger);    // add this
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    ...
}
``` [3](#0-2) [4](#0-3) 

---

### Proof of Concept

1. Deploy `RSETHPoolV2` behind a proxy.
2. Call `initialize(address(0), someValidBridger, validWrsETH, feeBps, validOracle)`.
3. The call succeeds — no revert.
4. `DEFAULT_ADMIN_ROLE` is now held by `address(0)`.
5. Attempt to call `reinitialize(newL2Bridge, newL1Vault, newMessenger)` from any EOA → reverts with `AccessControl: account 0x... is missing role 0x00...`.
6. Attempt to grant `DEFAULT_ADMIN_ROLE` to a recovery address → reverts for the same reason.
7. The pool is permanently unmanageable; any ETH deposited by users that requires a bridge update to be withdrawn is frozen. [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L152-168)
```text
    function reinitialize(
        address _l2Bridge,
        address _l1VaultETHForL2Chain,
        address _messenger
    )
        external
        reinitializer(2)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(_l2Bridge);
        UtilLib.checkNonZeroAddress(_l1VaultETHForL2Chain);
        UtilLib.checkNonZeroAddress(_messenger);

        l2Bridge = _l2Bridge;
        l1VaultETHForL2Chain = _l1VaultETHForL2Chain;
        messenger = _messenger;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L176-198)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
    }
```

**File:** contracts/LRTConfig.sol (L49-51)
```text
    function initialize(address admin, address stETH, address ethX, address rsETH_) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(rsETH_);
```

**File:** contracts/king-protocol/TokenSwap.sol (L120-123)
```text
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(manager);
        UtilLib.checkNonZeroAddress(_kingProtocol);
        UtilLib.checkNonZeroAddress(_kingToken);
```
