### Title
Missing Zero-Address Validation for `admin` and `bridger` in `initialize()` - (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
The `initialize()` functions in `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, and `RSETHPoolV3ExternalBridge` accept `admin` and `bridger` address parameters but do not validate them against `address(0)` before granting critical roles. If `admin` is set to `address(0)` at deployment, the contract becomes permanently unmanageable — no one can pause it, update fees, or perform any admin-gated operation — permanently freezing user funds deposited into the pool.

### Finding Description
In all three pool contracts, the `initialize()` function checks `_wrsETH` and `_rsETHOracle` for zero addresses via `UtilLib.checkNonZeroAddress()`, but omits the same check for `admin` and `bridger`:

```solidity
// RSETHPoolV2.sol initialize() — lines 186–193
UtilLib.checkNonZeroAddress(_wrsETH);       // checked
UtilLib.checkNonZeroAddress(_rsETHOracle);  // checked
// admin and bridger are NOT checked
_grantRole(DEFAULT_ADMIN_ROLE, admin);      // admin could be address(0)
_setupRole(BRIDGER_ROLE, admin);
_setupRole(BRIDGER_ROLE, bridger);          // bridger could be address(0)
```

The same pattern is replicated verbatim in `RSETHPoolV2ExternalBridge.sol` and `RSETHPoolV3ExternalBridge.sol`. [1](#0-0) [2](#0-1) [3](#0-2) 

By contrast, other contracts in the same codebase (e.g., `KernelVaultETH`, `L1Vault`, `RSETHPoolNoWrapper`) consistently apply `UtilLib.checkNonZeroAddress()` to every address parameter including `admin`. [4](#0-3) [5](#0-4) 

### Impact Explanation
If `admin = address(0)` is passed at initialization:
- `DEFAULT_ADMIN_ROLE` is granted to `address(0)`, meaning no real account holds admin control.
- No one can call `pause()`, `setFee`, or any `onlyRole(DEFAULT_ADMIN_ROLE)` function.
- User ETH deposited via `deposit()` (which mints pool-local rsETH) cannot be recovered or paused in an emergency.
- The contract is permanently unmanageable, constituting a permanent freeze of user funds.

**Impact: Medium — Temporary/Permanent freezing of funds** (proxy upgrade path may exist, but contract-level admin is irrecoverably lost).

### Likelihood Explanation
This requires a deployer to pass `address(0)` as `admin` — a realistic human error during deployment, especially given that the same `initialize()` signature is reused across three contracts. The absence of a guard makes this a latent deployment risk with no on-chain protection.

### Recommendation
Add `UtilLib.checkNonZeroAddress()` for `admin` and `bridger` in all three `initialize()` functions, consistent with the pattern used elsewhere in the codebase:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,
    address _rsETHOracle
) external initializer {
    UtilLib.checkNonZeroAddress(admin);     // ADD
    UtilLib.checkNonZeroAddress(bridger);   // ADD
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    ...
}
```

### Proof of Concept
1. Deploy `RSETHPoolV2` proxy and call `initialize(address(0), address(0), validWrsETH, feeBps, validOracle)`.
2. Initialization succeeds — no revert.
3. `DEFAULT_ADMIN_ROLE` is held only by `address(0)`.
4. Call `pause()` from any real account → reverts with `AccessControl` error.
5. Users deposit ETH; pool mints rsETH. No admin can ever pause or recover the contract.
6. Funds are permanently frozen with no recovery path at the contract level. [6](#0-5)

### Citations

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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L268-275)
```text
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L340-347)
```text
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L156-160)
```text
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_operator);
        UtilLib.checkNonZeroAddress(_kernel);
        UtilLib.checkNonZeroAddress(_kernelOftAdapter);
        UtilLib.checkNonZeroAddress(_receiver);
```

**File:** contracts/utils/UtilLib.sol (L11-13)
```text
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```
