### Title
Unvalidated `feeBps` in `initialize()` Enables Temporary Deposit DoS — (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

`RSETHPoolV3.initialize()` accepts `_feeBps` from the deployer and stores it without any bounds check. The post-deployment setter `setFeeBps()` enforces a strict 10% cap (`_feeBps > 1000` reverts). If `feeBps > 10_000` is written at initialization, every subsequent call to `deposit()` reverts due to arithmetic underflow in `viewSwapRsETHAmountAndFee()`, freezing all user deposits until the admin manually corrects the value.

---

### Finding Description

In `RSETHPoolV3.initialize()`, the `_feeBps` parameter is stored directly with no validation:

```solidity
// contracts/pools/RSETHPoolV3.sol  initialize()
feeBps = _feeBps;   // no bounds check
``` [1](#0-0) 

The post-deployment setter enforces a hard cap:

```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // max 10 %
    feeBps = _feeBps;
``` [2](#0-1) 

Every deposit path calls `viewSwapRsETHAmountAndFee()`:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;   // underflows when feeBps > 10_000
``` [3](#0-2) 

When `feeBps > 10_000`, `fee > amount`, and the unchecked subtraction reverts under Solidity 0.8 checked arithmetic. The `limitDailyMint` modifier also calls `viewSwapRsETHAmountAndFee()` before the deposit body executes, so the revert occurs even before any state change. [4](#0-3) 

The same pattern is present in every pool variant that stores `feeBps` in `initialize()` without validation:
- `RSETHPoolV3ExternalBridge.initialize()` [5](#0-4) 
- `RSETHPoolV3WithNativeChainBridge.initialize()` [6](#0-5) 
- `RSETHPoolNoWrapper.initialize()` [7](#0-6) 
- `AGETHPoolV3.initialize()` [8](#0-7) 

---

### Impact Explanation

If `feeBps` is initialized with any value `> 10_000` (e.g., deployer confuses raw percentage `100` with basis-point value `10_000`, or sets `20_000` intending 20%), every call to `deposit()` (ETH or token) reverts. No user can deposit ETH or supported LSTs into the pool. Funds already in the pool are not at risk of theft, but the pool is completely non-functional for depositors until the admin calls `setFeeBps()` with a corrected value.

**Impact: Medium — Temporary freezing of funds (deposit path).**

---

### Likelihood Explanation

The deployer must supply `_feeBps` as a raw `uint256`. The setter enforces `<= 1000` (10%), but the initializer has no guard. A deployer who intends to set a 5% fee and passes `5000` instead of `500`, or who passes a percentage integer `100` instead of `10_000`, will silently brick the pool. The inconsistency between the setter's documented cap and the initializer's absence of any cap makes this a realistic misconfiguration risk during deployment of new pool instances.

**Likelihood: Low** (requires a deployment-time mistake), but the consequence is immediate and affects all users of the newly deployed pool.

---

### Recommendation

Apply the same bounds check in `initialize()` that is already enforced in `setFeeBps()`:

```solidity
function initialize(..., uint256 _feeBps, ...) external initializer {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // mirror setFeeBps guard
    ...
    feeBps = _feeBps;
}
```

Apply the same fix to all pool variants listed above.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` with `_feeBps = 20_000` (deployer intends "20%" but passes raw 20 000).
2. Any user calls `deposit{value: 1 ether}("ref")`.
3. `limitDailyMint` modifier calls `viewSwapRsETHAmountAndFee(1 ether, ETH_IDENTIFIER)`.
4. `fee = 1e18 * 20_000 / 10_000 = 2e18 > 1e18`.
5. `amountAfterFee = 1e18 - 2e18` → Solidity 0.8 checked arithmetic reverts with arithmetic underflow.
6. All deposits revert. Pool is non-functional until admin calls `setFeeBps(500)`.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L229-229)
```text
        feeBps = _feeBps;
```

**File:** contracts/pools/RSETHPoolV3.sol (L300-301)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L330-352)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L245-268)
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

**File:** contracts/agETH/AGETHPoolV3.sol (L76-101)
```text
    function initialize(
        address admin,
        address bridger,
        address _agETH,
        uint256 _feeBps,
        address _agETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_agETH);
        UtilLib.checkNonZeroAddress(_agETHOracle);

        __ERC20_init("agETH", "agETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        agETH = IERC20AgETH(_agETH);
        feeBps = _feeBps;
        agETHOracle = _agETHOracle;
        isEthDepositEnabled = true;
    }
```
