### Title
`RSETH.initialize()` Does Not Set `maxMintAmountPerDay`, Permanently Blocking All rsETH Minting Until Manually Corrected - (File: contracts/RSETH.sol)

### Summary
`RSETH.initialize()` and `RSETH.reinitialize()` both fail to assign a value to `maxMintAmountPerDay`, leaving it at its default of zero. The `checkDailyMintLimit` modifier unconditionally reverts whenever `maxMintAmountPerDay == 0` and `amount > 0`, meaning every call to `RSETH.mint()` — and therefore every user deposit through `LRTDepositPool` — will revert until a manager separately calls `setMaxMintAmountPerDay()`.

### Finding Description
`RSETH.sol` introduces a daily minting cap enforced by the `checkDailyMintLimit` modifier:

```solidity
modifier checkDailyMintLimit(uint256 amount) {
    if (block.timestamp >= periodStartTime + 1 days) {
        currentPeriodMintedAmount = 0;
        periodStartTime = getCurrentPeriodStartTime();
    }
    if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
        revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
    }
    currentPeriodMintedAmount += amount;
    _;
}
``` [1](#0-0) 

When `maxMintAmountPerDay` is zero (its Solidity default), the condition `0 + amount > 0` is always `true` for any non-zero `amount`, causing an unconditional revert.

Neither `initialize()` nor `reinitialize()` assigns `maxMintAmountPerDay`: [2](#0-1) [3](#0-2) 

The only setter is `setMaxMintAmountPerDay()`, a separate manager call that must be invoked post-deployment: [4](#0-3) 

The `mint()` function, which is the sole path for issuing rsETH, applies this modifier: [5](#0-4) 

`LRTDepositPool._mintRsETH()` calls `RSETH.mint()` as the final step of every user deposit: [6](#0-5) 

This means `depositETH()` and `depositAsset()` both revert for all users until `setMaxMintAmountPerDay` is called: [7](#0-6) [8](#0-7) 

Notably, the view function `remainingDailyMintLimit()` explicitly short-circuits on `maxMintAmountPerDay == 0`, confirming the developers are aware this state can exist — yet the modifier has no equivalent guard: [9](#0-8) 

### Impact Explanation
**Medium — Temporary freezing of funds.** The entire deposit mechanism of the protocol is non-functional from the moment of deployment until `setMaxMintAmountPerDay` is explicitly called by a manager. Every `depositETH` and `depositAsset` call reverts. While individual transactions revert cleanly (no ETH or LSTs are permanently lost), the protocol cannot deliver its core promised service — issuing rsETH in exchange for deposited assets — for the entire window between `initialize()` and the manual `setMaxMintAmountPerDay()` call. The `LRTOracle`'s protocol-fee minting path (`IRSETH.mint(treasury, ...)`) is also blocked during this window.

### Likelihood Explanation
**Medium.** The `reinitialize()` function was added specifically to set `periodStartTime` and `custodyAddress` as a second initialization step, demonstrating the pattern of multi-step initialization. A deployer following this pattern may reasonably assume `maxMintAmountPerDay` is handled elsewhere (e.g., in `reinitialize`) and omit the `setMaxMintAmountPerDay` call. The bug is silent — no event or revert signals the uninitialized state at deployment time — and only manifests when the first deposit is attempted.

### Recommendation
Set `maxMintAmountPerDay` to a non-zero value during initialization. The simplest fix is to add a `_maxMintAmountPerDay` parameter to `initialize()` (or `reinitialize()`) and assign it there, with a non-zero check:

```solidity
function initialize(address admin, address lrtConfigAddr, uint256 _maxMintAmountPerDay) external initializer {
    UtilLib.checkNonZeroAddress(admin);
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    if (_maxMintAmountPerDay == 0) revert InvalidMaxMintAmount();
    __ERC20_init("rsETH", "rsETH");
    __Pausable_init();
    lrtConfig = ILRTConfig(lrtConfigAddr);
    maxMintAmountPerDay = _maxMintAmountPerDay;
    emit UpdatedLRTConfig(lrtConfigAddr);
    emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
}
```

If the contract is already deployed, `setMaxMintAmountPerDay()` must be called immediately after deployment before any deposits are expected.

### Proof of Concept
1. Deploy `RSETH` proxy and call `initialize(admin, lrtConfigAddr)`. `maxMintAmountPerDay` is now `0`.
2. Call `reinitialize(periodStartTime, custodyAddress)`. `maxMintAmountPerDay` is still `0`.
3. Any address calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. `LRTDepositPool._mintRsETH(rsethAmountToMint)` calls `RSETH.mint(msg.sender, rsethAmountToMint)`.
5. `checkDailyMintLimit(rsethAmountToMint)` evaluates `0 + rsethAmountToMint > 0` → `true` → reverts with `DailyMintLimitExceeded(rsethAmountToMint, 0)`.
6. All deposits are blocked. The protocol cannot issue rsETH until a manager calls `setMaxMintAmountPerDay(nonZeroValue)`.

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

**File:** contracts/RSETH.sol (L265-266)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        if (maxMintAmountPerDay == 0) return 0;
```

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
