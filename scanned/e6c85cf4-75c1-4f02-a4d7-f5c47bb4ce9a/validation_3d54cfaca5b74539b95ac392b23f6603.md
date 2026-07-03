### Title
`feeBps` Set Without Upper Bound Validation During Initialization, Causing Deposit Freeze or Zero-rsETH Minting - (File: contracts/pools/RSETHPoolV3.sol, RSETHPoolV2.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV2NBA.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol, RSETHPool.sol)

---

### Summary

Every L2 pool contract in the LRT-rsETH codebase accepts a `_feeBps` parameter in its `initialize()` function and assigns it directly to `feeBps` without any upper-bound check. The corresponding `setFeeBps()` setter in each contract correctly enforces `if (_feeBps > 10_000) revert InvalidFeeAmount()`, but this guard is absent from the initializer. If `feeBps` is initialized at or above `10_000` (100%), all user deposits either silently mint 0 rsETH (at exactly 10,000 BPS) or revert with an arithmetic underflow (above 10,000 BPS), permanently bricking the pool's deposit path until an admin corrects the value.

---

### Finding Description

All pool variants share the same pattern. In `RSETHPoolV3.initialize()`:

```solidity
function initialize(
    address admin,
    address bridger,
    address _wrsETH,
    uint256 _feeBps,       // ← no upper-bound check
    address _rsETHOracle,
    bool _isEthDepositEnabled
) external initializer {
    ...
    feeBps = _feeBps;      // ← stored unconditionally
    ...
}
```

The fee is consumed in `viewSwapRsETHAmountAndFee`:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // ← underflows if feeBps > 10_000
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Two distinct failure modes arise:

1. **`feeBps == 10_000` (100%)**: `fee == amount`, so `amountAfterFee == 0` and `rsETHAmount == 0`. The user's ETH/tokens are accepted by the pool, `feeEarnedInETH` is incremented by the full deposit, but the user receives 0 wrsETH/rsETH. The deposited value is permanently captured as protocol fee, withdrawable only by `BRIDGER_ROLE`.

2. **`feeBps > 10_000` (> 100%)**: `fee > amount`, causing `amount - fee` to underflow. Solidity 0.8.x reverts on underflow, so every call to `deposit()` reverts. The pool is completely non-functional for depositors until an admin calls `setFeeBps()` with a valid value.

The `setFeeBps()` setter in every affected contract correctly guards against this:

```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(TIMELOCK_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    feeBps = _feeBps;
}
```

The inconsistency between the setter (guarded) and the initializer (unguarded) is the root cause.

---

### Impact Explanation

- **`feeBps > 10_000`**: Every `deposit()` call reverts due to arithmetic underflow in `viewSwapRsETHAmountAndFee`. No user can deposit ETH or supported tokens. This is a **temporary freeze of funds** (the pool is bricked until admin corrects `feeBps` via `setFeeBps()`). Impact: **Medium**.
- **`feeBps == 10_000`**: Users deposit ETH/tokens and receive 0 rsETH/wrsETH. Their full deposit is silently captured as fee. Impact: **Critical** (direct theft of deposited user funds).

The most realistic deployment mistake is a misconfiguration (e.g., entering `10000` intending 100 BPS = 1%, or `500` intending 5% but accidentally entering `5000`), which maps directly to the freeze scenario.

---

### Likelihood Explanation

The `initialize()` function is called exactly once per proxy deployment, typically by the deployer script. A misconfiguration at this step (e.g., passing `feeBps = 10_000` when intending 100 BPS, or any value above 10,000) is a realistic human error, especially given that the setter enforces the bound but the initializer does not, creating a false sense of safety. The protocol has eight affected pool variants, increasing the surface area for this mistake across deployments.

---

### Recommendation

Add the same upper-bound check present in `setFeeBps()` to every `initialize()` function:

```solidity
if (_feeBps > 10_000) revert InvalidFeeAmount();
feeBps = _feeBps;
```

Apply this to all affected contracts: `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolNoWrapper`, and `RSETHPool`.

---

### Proof of Concept

**Root cause — initializer stores `feeBps` without validation:**

`RSETHPoolV3.initialize()` assigns `feeBps = _feeBps` with no bound check: [1](#0-0) 

`RSETHPoolV2.initialize()` has the same pattern: [2](#0-1) 

`RSETHPoolNoWrapper.initialize()` has the same pattern: [3](#0-2) 

**Fee calculation that breaks when `feeBps >= 10_000`:**

`viewSwapRsETHAmountAndFee` in `RSETHPoolV3`: [4](#0-3) 

**Contrast — `setFeeBps()` correctly validates the bound:**

`RSETHPoolV2.setFeeBps()`: [5](#0-4) 

`RSETHPoolV2NBA.setFeeBps()`: [6](#0-5) 

**Attack path:**

1. Admin deploys a pool proxy and calls `initialize(..., _feeBps = 10_000, ...)` (e.g., intending 100 BPS but entering the wrong value).
2. `feeBps` is stored as `10_000` with no revert.
3. Any user calls `deposit()` with `amount > 0`.
4. `viewSwapRsETHAmountAndFee` computes `fee = amount * 10_000 / 10_000 = amount`, `amountAfterFee = 0`, `rsETHAmount = 0`.
5. The user's ETH is accepted; `feeEarnedInETH += amount`; user receives 0 wrsETH.
6. If `feeBps > 10_000`, step 4 underflows and every deposit reverts, freezing the pool.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L207-231)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
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
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
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

**File:** contracts/pools/RSETHPoolV2.sol (L303-307)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(TIMELOCK_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L190-217)
```text
    function initialize(
        address admin,
        address manager,
        address _rsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(manager);
        UtilLib.checkNonZeroAddress(_rsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(BRIDGER_ROLE, manager);

        rsETH = IERC20(_rsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L163-167)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```
