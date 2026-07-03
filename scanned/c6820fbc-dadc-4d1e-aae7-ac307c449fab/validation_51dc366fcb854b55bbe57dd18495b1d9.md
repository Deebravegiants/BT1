### Title
Uninitialized `maxMintAmountPerDay` Permanently Blocks All rsETH Minting Until Admin Intervenes - (File: contracts/RSETH.sol)

### Summary
`RSETH.sol` declares `maxMintAmountPerDay` as a state variable that defaults to `0`. The `checkDailyMintLimit` modifier applied to `mint()` unconditionally reverts for any non-zero amount when this variable is `0`. Because neither `initialize()` nor `reinitialize()` sets this variable, every call to `RSETH.mint()` — and therefore every user deposit through `LRTDepositPool` — reverts until an LRT manager separately calls `setMaxMintAmountPerDay()`.

### Finding Description
`RSETH.sol` introduces a daily mint cap enforced by the `checkDailyMintLimit` modifier:

```solidity
// contracts/RSETH.sol lines 50-51
if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
    revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
}
``` [1](#0-0) 

`maxMintAmountPerDay` is declared as a plain `uint256` storage variable and therefore initializes to `0`: [2](#0-1) 

The `initialize()` function does not set it: [3](#0-2) 

The `reinitialize()` (version 2) also does not set it — it only sets `periodStartTime` and `custodyAddress`: [4](#0-3) 

The only setter is a standalone manager function: [5](#0-4) 

The `mint()` function applies `checkDailyMintLimit`: [6](#0-5) 

When `maxMintAmountPerDay == 0`, the condition `currentPeriodMintedAmount + amount > 0` is true for every non-zero `amount`, so every mint call reverts.

`LRTDepositPool._mintRsETH()` is the downstream caller: [7](#0-6) 

This means every user deposit that reaches `_mintRsETH()` reverts until `setMaxMintAmountPerDay()` is called.

### Impact Explanation
**Medium — Temporary freezing of funds.**

All user deposits through `LRTDepositPool` (both LST and ETH paths) are completely blocked from the moment the upgraded `RSETH` contract is live until an LRT manager calls `setMaxMintAmountPerDay()`. No user can receive rsETH in exchange for deposited assets during this window. The freeze is temporary only if the manager acts promptly; if the call is delayed or forgotten, the freeze extends indefinitely.

### Likelihood Explanation
**Medium.** The variable is silently uninitialized across both `initialize()` and `reinitialize()`. Any deployment or upgrade of `RSETH` that does not immediately follow with a `setMaxMintAmountPerDay()` call produces the broken state. There is no on-chain enforcement requiring the setter to be called before minting is attempted, and no revert guard in `initialize()` to catch the omission.

### Recommendation
Set `maxMintAmountPerDay` to a non-zero value inside `initialize()` (or the relevant `reinitialize()`) so that minting is never gated by an uninitialized zero. Alternatively, add a guard in `checkDailyMintLimit` that skips the cap check when `maxMintAmountPerDay == 0` (treating zero as "uncapped"), mirroring the fix applied in the referenced TRST-H-6 report.

### Proof of Concept
1. Deploy (or upgrade to) the current `RSETH` contract. `maxMintAmountPerDay` is `0`.
2. A user deposits any supported asset into `LRTDepositPool`.
3. `LRTDepositPool._mintRsETH()` calls `RSETH.mint(user, amount)`.
4. `checkDailyMintLimit(amount)` evaluates `0 + amount > 0` → `true` → reverts with `DailyMintLimitExceeded(amount, 0)`.
5. The deposit transaction reverts. No rsETH is minted. The user's assets are returned (not lost), but the protocol is non-functional for all depositors until `setMaxMintAmountPerDay()` is called by an LRT manager.

### Citations

**File:** contracts/RSETH.sol (L18-19)
```text
    /// @notice Maximum amount that can be minted in a 24-hour period
    uint256 public maxMintAmountPerDay;
```

**File:** contracts/RSETH.sol (L50-52)
```text
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
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

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
