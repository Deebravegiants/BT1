### Title
`dailyMintLimit` Uninitialized to Zero Causes All Deposits to Always Revert - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `dailyMintLimit` state variable defaults to `0` and is never set inside `initialize()`. The `limitDailyMint` modifier, which guards every `deposit()` entry point, unconditionally reverts with `DailyMintLimitExceeded` for any non-zero deposit when `dailyMintLimit == 0`, blocking all user deposits until an admin manually calls `setDailyMintLimit()`.

---

### Finding Description

`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` all declare `dailyMintLimit` as a plain storage variable that defaults to `0`: [1](#0-0) [2](#0-1) [3](#0-2) 

None of the `initialize()` functions assign a value to `dailyMintLimit`: [4](#0-3) 

The `limitDailyMint` modifier is applied to both `deposit()` overloads in all three contracts: [5](#0-4) 

The critical check inside the modifier: [6](#0-5) 

When `dailyMintLimit == 0`, the condition `dailyMintAmount + rsETHAmount > 0` is always `true` for any non-zero deposit, so every call to `deposit()` reverts with `DailyMintLimitExceeded`.

The `startTimestamp` is also `0` by default. With `startTimestamp == 0`, the guard `block.timestamp < startTimestamp` evaluates to `false` (since `block.timestamp > 0`), so execution reaches the limit check and reverts there. The `getCurrentDay()` arithmetic `(block.timestamp - 0) / 1 days` does not underflow, but it produces a large day number that resets `dailyMintAmount` to `0` on every call, making the limit check `0 + rsETHAmount > 0` — always true.

The value is only set in a separate `reinitialize()` call (reinitializer(2) for V3/V3WithNativeChainBridge, reinitializer(4) for ExternalBridge): [7](#0-6) 

If this reinitializer is not called after deployment, the contract is permanently stuck in a state where deposits are impossible. A `setDailyMintLimit()` setter exists but requires `DEFAULT_ADMIN_ROLE` and must be invoked manually: [8](#0-7) 

---

### Impact Explanation

All user-facing `deposit()` functions revert for every non-zero amount until an admin intervenes. Users cannot deposit ETH or supported tokens to receive `wrsETH`/`rsETH`. This constitutes a **temporary freezing of funds** (deposits blocked), matching the "Medium. Temporary freezing of funds" impact category. The freeze is not permanent because `setDailyMintLimit()` can be called by the admin, but until that happens the core protocol function is completely non-operational.

---

### Likelihood Explanation

Any fresh deployment of `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, or `RSETHPoolV3WithNativeChainBridge` where the corresponding `reinitialize()` for the daily mint limit is not called atomically with `initialize()` will exhibit this behavior. Given the multi-step upgrade pattern used across all three contracts (up to reinitializer(6) in `RSETHPoolV3ExternalBridge`), the window between `initialize()` and the relevant `reinitialize()` call is a realistic deployment scenario. No attacker action is required — the state is broken by default.

---

### Recommendation

Initialize `dailyMintLimit` to a sensible non-zero default directly inside `initialize()`, or add a non-zero check on `dailyMintLimit` in the `limitDailyMint` modifier that skips the limit enforcement when the variable has not yet been configured (treating `0` as "no limit set yet"). For example:

```solidity
modifier limitDailyMint(uint256 amount, address token) {
    if (dailyMintLimit == 0) revert DailyMintLimitNotSet(); // or skip enforcement
    ...
}
```

Alternatively, require `dailyMintLimit` to be passed as a parameter to `initialize()` and validated as non-zero there, mirroring the validation already present in `reinitialize()`.

---

### Proof of Concept

1. Deploy `RSETHPoolV3` proxy and call `initialize(admin, bridger, wrsETH, feeBps, oracle, true)`.
2. Do **not** call `reinitialize(dailyMintLimit, startTimestamp)`.
3. Any user calls `deposit{value: 1 ether}("ref")`.
4. Inside `limitDailyMint`:
   - `block.timestamp < 0` → `false` (passes).
   - `viewSwapRsETHAmountAndFee(1 ether)` returns `rsETHAmount > 0`.
   - `getCurrentDay()` returns `block.timestamp / 1 days` (large number > `lastMintDay == 0`), so `dailyMintAmount` resets to `0`.
   - `0 + rsETHAmount > dailyMintLimit` → `rsETHAmount > 0` → **always true**.
   - Reverts with `DailyMintLimitExceeded`.
5. All deposits are blocked until admin calls `setDailyMintLimit(nonZeroValue)`. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L51-51)
```text
    uint256 public dailyMintLimit;
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L179-198)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(2)
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

**File:** contracts/pools/RSETHPoolV3.sol (L207-232)
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
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L339-341)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L605-611)
```text
    function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }
        dailyMintLimit = _dailyMintLimit;
        emit DailyMintLimitSet(_dailyMintLimit);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L67-67)
```text
    uint256 public dailyMintLimit;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L57-57)
```text
    uint256 public dailyMintLimit;
```
