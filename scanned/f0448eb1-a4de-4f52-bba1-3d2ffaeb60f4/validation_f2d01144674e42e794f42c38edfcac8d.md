### Title
`maxMintAmountPerDay` Defaults to Zero Post-Deployment, Permanently Blocking All rsETH Minting - (File: contracts/RSETH.sol)

### Summary
`RSETH.sol` introduces a `maxMintAmountPerDay` daily mint cap enforced by the `checkDailyMintLimit` modifier. Neither `initialize()` nor `reinitialize()` sets this value, so it defaults to `0`. When `maxMintAmountPerDay == 0`, the modifier's comparison `currentPeriodMintedAmount + amount > maxMintAmountPerDay` evaluates to `amount > 0`, which is always true for any real deposit. Every call to `mint()` reverts with `DailyMintLimitExceeded` until a manager explicitly calls `setMaxMintAmountPerDay` with a non-zero value.

### Finding Description
`RSETH.initialize()` sets up the ERC-20 token and role configuration but never assigns `maxMintAmountPerDay`: [1](#0-0) 

`reinitialize()` (version 2) sets `periodStartTime` and `custodyAddress` but also omits `maxMintAmountPerDay`: [2](#0-1) 

The `checkDailyMintLimit` modifier then enforces: [3](#0-2) 

With `maxMintAmountPerDay == 0`, the condition `currentPeriodMintedAmount + amount > 0` is always `true` for any `amount > 0`, causing an unconditional revert. The `mint()` function, which is the only path to issue rsETH to depositors, applies this modifier: [4](#0-3) 

The setter `setMaxMintAmountPerDay` is the only remedy, but it is never called during initialization: [5](#0-4) 

This is the direct analog to the external report: a security-critical parameter (`timeLockPeriod` / `maxMintAmountPerDay`) is left at its default value of `0` after deployment because no initialization path sets it, causing the guarded function to behave incorrectly — in this case, blocking all minting rather than bypassing a time lock.

### Impact Explanation
Every user deposit into `LRTDepositPool` that triggers `RSETH.mint()` will revert. No rsETH can be issued to any depositor. The contract fails to deliver its core promised return (rsETH in exchange for deposited assets). User funds are not lost (the deposit transaction reverts atomically), but the protocol is non-functional for minting until the manager intervenes.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
This condition exists from the moment the contract is deployed or upgraded. Any depositor who calls `LRTDepositPool.depositAsset()` (or equivalent) before `setMaxMintAmountPerDay` is called will have their transaction revert. The window of exposure is the entire period between deployment and the first manager call to `setMaxMintAmountPerDay`, which is not enforced or guaranteed by the contract itself.

### Recommendation
- **Short term:** Set `maxMintAmountPerDay` to a non-zero value inside `initialize()` (or the relevant `reinitialize()`) so the contract is functional immediately upon deployment.
- **Long term:** Add a `require(_maxMintAmountPerDay > 0)` guard inside `setMaxMintAmountPerDay` to prevent the manager from accidentally resetting it to `0` and re-blocking all minting.

### Proof of Concept
1. Deploy `RSETH` and call `initialize(admin, lrtConfigAddr)`. `maxMintAmountPerDay` is `0`.
2. Optionally call `reinitialize(periodStartTime, custodyAddress)`. `maxMintAmountPerDay` remains `0`.
3. A user deposits ETH into `LRTDepositPool`, which calls `RSETH.mint(user, amount)`.
4. `checkDailyMintLimit(amount)` evaluates `0 + amount > 0` → `true` → reverts with `DailyMintLimitExceeded(amount, 0)`.
5. The deposit reverts. No rsETH is minted. The protocol is non-functional until `setMaxMintAmountPerDay(nonZeroValue)` is called by the manager.

### Citations

**File:** contracts/RSETH.sol (L42-56)
```text
    modifier checkDailyMintLimit(uint256 amount) {
        // Check if we need to reset the period if it has been more than 24 hours
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
        _;
    }
```

**File:** contracts/RSETH.sol (L96-104)
```text
    function initialize(address admin, address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(lrtConfigAddr);

        __ERC20_init("rsETH", "rsETH");
        __Pausable_init();
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/RSETH.sol (L109-117)
```text
    function reinitialize(uint256 _periodStartTime, address _custodyAddress) external reinitializer(2) onlyLRTManager {
        if (_periodStartTime > block.timestamp || _periodStartTime <= block.timestamp - 1 days) {
            revert PeriodStartTimeShouldBeWithin24Hours();
        }
        periodStartTime = _periodStartTime;
        emit PeriodStartTimeSet(_periodStartTime);

        _setCustodyAddress(_custodyAddress);
    }
```

**File:** contracts/RSETH.sol (L125-128)
```text
    function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
        maxMintAmountPerDay = _maxMintAmountPerDay;
        emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
    }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }
```
