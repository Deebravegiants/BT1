### Title
Missing Zero-Address Checks for Critical Initialization Parameters in `RSETHPool.initialize` - (File: contracts/pools/RSETHPool.sol)

---

### Summary

`RSETHPool.initialize` accepts seven address parameters but only validates two of them (`_rsETH`, `_wstETH`) with `UtilLib.checkNonZeroAddress`. The parameters `admin`, `manager`, `_rsETHOracle`, and `_wstETH_ETHOracle` receive no zero-address guard. If any of these are set to `address(0)` at deployment, the pool is permanently broken with no recovery path, because `initialize` is one-shot (`initializer` modifier).

---

### Finding Description

In `RSETHPool.initialize`, only `_rsETH` and `_wstETH` are validated: [1](#0-0) 

The remaining four address parameters are silently accepted and stored or used without any guard:

- `admin` → `_grantRole(DEFAULT_ADMIN_ROLE, admin)` — if `address(0)`, no real account holds `DEFAULT_ADMIN_ROLE`
- `manager` → `_setupRole(LEGACY_MANAGER_ROLE, manager)` — if `address(0)`, role is granted to the zero address
- `_rsETHOracle` → stored as `rsETHOracle` and called in `getRate()` as `IOracle(rsETHOracle).getRate()`
- `_wstETH_ETHOracle` → stored as `legacyWstETH_ETHOracle` [2](#0-1) 

The `getRate()` function is called unconditionally inside both `viewSwapRsETHAmountAndFee` overloads: [3](#0-2) 

Both public `deposit()` entry points call `viewSwapRsETHAmountAndFee`, so a zero `rsETHOracle` causes every deposit to revert: [4](#0-3) 

---

### Impact Explanation

**Permanent freezing of funds / permanent loss of admin control.**

If `_rsETHOracle = address(0)` is passed at initialization:
- Every call to `deposit()` (ETH or token path) reverts because `IOracle(address(0)).getRate()` is an external call to the zero address, which returns no code and causes a revert.
- Any rsETH pre-loaded into the pool for liquidity is permanently locked — no user can receive it, and no admin can rescue it if `admin` is also zero.

If `admin = address(0)`:
- `DEFAULT_ADMIN_ROLE` is granted to `address(0)`, meaning no real account can call role-gated admin functions (`setOracle`, `pause`, `addSupportedToken`, `withdrawFees`, etc.).
- The contract is permanently unmanageable.

Combined, both zero values produce a permanently bricked pool with locked rsETH liquidity — matching the **permanent freezing of funds** impact class.

---

### Likelihood Explanation

Deployment misconfiguration is a realistic risk for upgradeable proxy deployments where initialization scripts are written manually. The absence of a revert guard means a typo or copy-paste error in the deployment script silently succeeds on-chain. Because `initializer` prevents re-initialization, there is no recovery. The Linea TokenBridge audit identified this exact class of error as exploitable in production.

---

### Recommendation

Add `UtilLib.checkNonZeroAddress` for all address parameters in `RSETHPool.initialize`:

```solidity
function initialize(
    address admin,
    address manager,
    address _rsETH,
    address _wstETH,
    uint256 _feeBps,
    address _rsETHOracle,
    address _wstETH_ETHOracle
) external initializer {
    UtilLib.checkNonZeroAddress(admin);
    UtilLib.checkNonZeroAddress(manager);
    UtilLib.checkNonZeroAddress(_rsETH);
    UtilLib.checkNonZeroAddress(_wstETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    UtilLib.checkNonZeroAddress(_wstETH_ETHOracle);
    // ... rest of initialization
}
```

Apply the same pattern to `RSETHPoolV2.initialize`, which similarly omits checks for `admin` and `bridger`. [5](#0-4) 

---

### Proof of Concept

1. Deploy `RSETHPool` proxy and call `initialize` with `_rsETHOracle = address(0)` and `admin = address(0)` (all other params valid).
2. The call succeeds — no revert, no event indicating misconfiguration.
3. Pre-load the pool with rsETH liquidity (as is normal for pool operation).
4. Any user calls `deposit{value: 1 ether}("")`.
5. Execution reaches `viewSwapRsETHAmountAndFee` → `getRate()` → `IOracle(address(0)).getRate()` → reverts.
6. No admin can call `setOracle` to fix `rsETHOracle` because `DEFAULT_ADMIN_ROLE` belongs to `address(0)`.
7. All rsETH in the pool is permanently frozen. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPool.sol (L222-251)
```text
    function initialize(
        address admin,
        address manager,
        address _rsETH,
        address _wstETH,
        uint256 _feeBps,
        address _rsETHOracle,
        address _wstETH_ETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_rsETH);
        UtilLib.checkNonZeroAddress(_wstETH);

        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        // legacy settings
        _setupRole(LEGACY_MANAGER_ROLE, admin);
        _setupRole(LEGACY_MANAGER_ROLE, manager);

        wrsETH = IERC20Upgradeable(_rsETH);
        legacyWstETH = IERC20Upgradeable(_wstETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        legacyWstETH_ETHOracle = _wstETH_ETHOracle;
    }
```

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
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

**File:** contracts/utils/UtilLib.sol (L11-13)
```text
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```
