### Title
`checkDailyMintLimit` Blocks All Minting When `maxMintAmountPerDay` Is Zero — (`contracts/RSETH.sol`)

### Summary

The `checkDailyMintLimit` modifier in `RSETH.sol` does not handle `maxMintAmountPerDay == 0` as a sentinel "no limit" case. Because `maxMintAmountPerDay` defaults to `0` after `initialize()` and `reinitialize()` (neither sets it), and because `setMaxMintAmountPerDay` accepts `0` without validation, any state where `maxMintAmountPerDay == 0` causes every call to `mint()` to revert, blocking all deposits into `LRTDepositPool`.

### Finding Description

`RSETH.initialize()` does not set `maxMintAmountPerDay`; it remains the default `uint256` value of `0`. The `reinitialize()` function also does not set it. The only setter is:

```solidity
// contracts/RSETH.sol L125-128
function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
    maxMintAmountPerDay = _maxMintAmountPerDay;
    emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
}
```

No validation prevents `_maxMintAmountPerDay == 0`. The enforcement modifier is:

```solidity
// contracts/RSETH.sol L42-56
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
```

When `maxMintAmountPerDay == 0`, the condition `currentPeriodMintedAmount + amount > 0` reduces to `amount > 0`, which is always true for any real deposit. Every call to `mint()` reverts with `DailyMintLimitExceeded`.

`mint()` is applied with `checkDailyMintLimit`:

```solidity
// contracts/RSETH.sol L229-239
function mint(address to, uint256 amount)
    external
    onlyRole(LRTConstants.MINTER_ROLE)
    whenNotPaused
    checkDailyMintLimit(amount)
{
    _enforceNotBlocked(to);
    _mint(to, amount);
}
```

`LRTDepositPool._mintRsETH` calls `IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)`, so both `depositETH` and `depositAsset` revert whenever `maxMintAmountPerDay == 0`.

The `remainingDailyMintLimit()` view function also signals the ambiguity — it returns `0` when `maxMintAmountPerDay == 0`, rather than `type(uint256).max`, which would be the natural sentinel for "unlimited":

```solidity
// contracts/RSETH.sol L265-266
function remainingDailyMintLimit() external view returns (uint256) {
    if (maxMintAmountPerDay == 0) return 0;
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Impact Explanation

When `maxMintAmountPerDay == 0`, every call to `LRTDepositPool.depositETH` and `LRTDepositPool.depositAsset` reverts. No rsETH is minted and no assets are accepted. The contract fails to deliver its core promised return — liquid restaking tokens in exchange for deposited ETH/LSTs — without any loss of already-held funds.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation

Two realistic paths reach this state:

1. **Default post-deployment state**: `initialize()` and `reinitialize()` never set `maxMintAmountPerDay`. Until `setMaxMintAmountPerDay` is called as a separate step, the contract is live but non-functional for all depositors.
2. **Manager sets to zero**: `setMaxMintAmountPerDay(0)` is accepted without revert, silently re-entering the broken state.

Path 1 is a deployment sequencing gap; path 2 requires manager action. Neither requires an unprivileged attacker, but path 1 is reachable by any depositor during the window between deployment and configuration.

**Likelihood: Low.**

### Recommendation

Add a sentinel bypass in `checkDailyMintLimit` so that `maxMintAmountPerDay == 0` means "no limit":

```solidity
modifier checkDailyMintLimit(uint256 amount) {
    if (maxMintAmountPerDay != 0) {
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }
        currentPeriodMintedAmount += amount;
    }
    _;
}
```

Alternatively, add `require(_maxMintAmountPerDay > 0)` in `setMaxMintAmountPerDay` and set a non-zero default in `initialize()`. Update `remainingDailyMintLimit()` to return `type(uint256).max` when `maxMintAmountPerDay == 0` to reflect the "unlimited" semantic consistently.

### Proof of Concept

1. Deploy `RSETH` and call `initialize(admin, lrtConfig)`. `maxMintAmountPerDay` is `0`.
2. Call `reinitialize(periodStartTime, custodyAddress)`. `maxMintAmountPerDay` remains `0`.
3. A depositor calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. `_mintRsETH` calls `IRSETH.mint(depositor, rsethAmount)`.
5. `checkDailyMintLimit` evaluates `0 + rsethAmount > 0` → `true` → reverts with `DailyMintLimitExceeded(rsethAmount, 0)`.
6. All deposits revert until `setMaxMintAmountPerDay` is called with a non-zero value. [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** contracts/RSETH.sol (L229-239)
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

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L684-690)
```text
    /// @dev private function to mint rseth
    /// @param rsethAmountToMint Amount of rseth minted
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
