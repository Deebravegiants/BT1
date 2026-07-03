Looking at the full contract, I need to trace the exact execution path when `reinitialize(4)` is never called.

### Title
Uninitialized `dailyMintLimit = 0` Blocks All Deposits When `reinitialize(4)` Is Skipped — (`contracts/pools/RSETHPoolV2ExternalBridge.sol`)

---

### Summary

If the admin upgrades to `RSETHPoolV2ExternalBridge` but never calls `reinitialize(4)`, `dailyMintLimit` and `startTimestamp` remain at their default value of `0`. Every subsequent call to `deposit()` will revert with `DailyMintLimitExceeded` because the `limitDailyMint` modifier unconditionally checks `dailyMintAmount + rsETHAmount > dailyMintLimit`, which is `rsETHAmount > 0` — always true for any non-zero deposit.

---

### Finding Description

`initialize()` does not set `dailyMintLimit` or `startTimestamp`. [1](#0-0) 

These values are only set by `reinitialize(uint256,uint256)`, which carries `reinitializer(4)`: [2](#0-1) 

`deposit()` unconditionally applies `limitDailyMint(msg.value)`: [3](#0-2) 

Inside `limitDailyMint`, the execution path when both values are `0`:

1. **`startTimestamp = 0`** — the guard `block.timestamp < startTimestamp` evaluates to `block.timestamp < 0`, which is always `false`. No revert here.
2. **`currentDay`** = `(block.timestamp - 0) / 1 days` ≈ 19,000+, which is always `> lastMintDay (0)`, so `dailyMintAmount` is reset to `0`.
3. **The fatal check**: `0 + rsETHAmount > 0` is `true` for any non-zero deposit → **`DailyMintLimitExceeded` revert**. [4](#0-3) 

---

### Impact Explanation

All calls to `deposit()` revert. No user can swap ETH for rsETH through this pool. The pool's core function is completely non-operational until the admin intervenes. This constitutes a **temporary freezing of funds** (deposits blocked) at **Medium** severity. It is temporary because `setDailyMintLimit()` is available to `DEFAULT_ADMIN_ROLE` at any time as a recovery path: [5](#0-4) 

---

### Likelihood Explanation

The `reinitialize(4)` function is a one-time upgrade step that must be called manually after deploying the new implementation. There is no on-chain enforcement that it was called before deposits are accepted. A missed or delayed upgrade transaction — a realistic operational scenario — triggers this state silently. The contract gives no indication to users why deposits are failing.

---

### Recommendation

Add a guard in `limitDailyMint` (or in `deposit` itself) that reverts with a descriptive error when `dailyMintLimit == 0`, making the uninitialized state explicit:

```solidity
modifier limitDailyMint(uint256 amount) {
    if (dailyMintLimit == 0) revert InvalidDailyMintLimit(); // <-- add this
    if (block.timestamp < startTimestamp) revert MintBeforeStartTimestamp();
    ...
}
```

Alternatively, set a non-zero default `dailyMintLimit` inside `initialize()` so the contract is functional immediately after deployment without requiring a separate reinitializer call.

---

### Proof of Concept

```solidity
// 1. Deploy proxy pointing to RSETHPoolV2ExternalBridge implementation
// 2. Call initialize(admin, bridger, wrsETH, feeBps, oracle) — does NOT set dailyMintLimit
// 3. Skip reinitialize(dailyMintLimit, startTimestamp)
// 4. Assert state: dailyMintLimit == 0, startTimestamp == 0

// 5. Any user attempts deposit:
pool.deposit{value: 1 ether}("ref");
// → reverts with DailyMintLimitExceeded
// because: 0 + rsETHAmount > 0 == true

// 6. Confirm no bypass exists for depositors
// 7. Admin calls setDailyMintLimit(X) → deposits resume (temporary, not permanent)
```

The revert path is deterministic and requires no special permissions or external state — any non-zero ETH deposit triggers it. [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L104-126)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L204-223)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(4)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }

        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }

        dailyMintLimit = _dailyMintLimit;
        startTimestamp = _startTimestamp;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L258-280)
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-289)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L605-611)
```text
    function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }
        dailyMintLimit = _dailyMintLimit;
        emit DailyMintLimitSet(_dailyMintLimit);
    }
```
