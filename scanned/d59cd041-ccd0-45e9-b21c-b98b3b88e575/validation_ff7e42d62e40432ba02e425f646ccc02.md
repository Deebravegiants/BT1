### Title
`getAssetCurrentLimit` Returns Non-Zero When `LRTDepositPool` Is Paused, Misleading Integrators - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getAssetCurrentLimit()` is the protocol's canonical "how much can be deposited" view function. When the contract is paused, it still returns a non-zero value, but every actual deposit path (`depositETH`, `depositAsset`) reverts due to `whenNotPaused`. Any off-chain component or on-chain integrator that queries `getAssetCurrentLimit` to decide whether to proceed with a deposit will receive a misleading answer.

### Finding Description

`LRTDepositPool` is pausable via OpenZeppelin's `PausableUpgradeable`: [1](#0-0) 

Both deposit entry points are gated by `whenNotPaused`: [2](#0-1) [3](#0-2) 

The view function `getAssetCurrentLimit` computes the remaining deposit capacity purely from on-chain accounting — it never inspects the pause state: [4](#0-3) 

When the contract is paused:
1. `getAssetCurrentLimit(asset)` returns `depositLimitByAsset(asset) - totalAssetDeposits` (a positive number).
2. Any call to `depositETH` or `depositAsset` reverts immediately at the `whenNotPaused` check.

The same inconsistency exists in `RSETH.remainingDailyMintLimit()`, which reports remaining mint capacity without checking the `RSETH` pause state, while `mint()` is gated by `whenNotPaused`: [5](#0-4) [6](#0-5) 

### Impact Explanation

Any smart contract or off-chain keeper that calls `getAssetCurrentLimit` (or `remainingDailyMintLimit`) to gate a deposit transaction will receive a non-zero "go ahead" signal and then have its deposit transaction revert. This breaks the expected contract between the view function and the action function. No funds are lost, but the contract fails to deliver its promised interface behavior.

**Impact: Low** — Contract fails to deliver promised returns, but doesn't lose value.

### Likelihood Explanation

The pause mechanism is an active operational control (callable by `PAUSER_ROLE`). Any integration — on-chain router, off-chain bot, or UI — that uses `getAssetCurrentLimit` as a pre-flight check will malfunction during any pause period. Pauses are expected to occur (e.g., during incidents), making this a realistic scenario.

### Recommendation

Override `getAssetCurrentLimit` in `LRTDepositPool` to return `0` when the contract is paused:

```solidity
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    if (paused()) return 0;
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
}
```

Similarly, `RSETH.remainingDailyMintLimit()` should return `0` when `RSETH` is paused:

```solidity
function remainingDailyMintLimit() external view returns (uint256) {
    if (paused()) return 0;
    if (maxMintAmountPerDay == 0) return 0;
    uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days)
        ? 0 : currentPeriodMintedAmount;
    return maxMintAmountPerDay > effectiveDailyMintAmount
        ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
}
```

### Proof of Concept

1. `PAUSER_ROLE` calls `LRTDepositPool.pause()`.
2. An integrator calls `LRTDepositPool.getAssetCurrentLimit(stETH)` — it returns, e.g., `1000 ether`.
3. The integrator calls `LRTDepositPool.depositAsset(stETH, 100 ether, ...)` — it reverts with `Pausable: paused`.
4. The view function's return value was inconsistent with the actual deposit capacity of `0`. [7](#0-6) [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L26-27)
```text
contract LRTDepositPool is ILRTDepositPool, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;
```

**File:** contracts/LRTDepositPool.sol (L76-84)
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
```

**File:** contracts/LRTDepositPool.sol (L99-108)
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
```

**File:** contracts/LRTDepositPool.sol (L349-351)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/RSETH.sol (L229-237)
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
```

**File:** contracts/RSETH.sol (L265-272)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        if (maxMintAmountPerDay == 0) return 0;

        // If we're on a new day but no mint has occurred yet, treat currentPeriodMintedAmount as 0
        uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days) ? 0 : currentPeriodMintedAmount;

        return maxMintAmountPerDay > effectiveDailyMintAmount ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
    }
```
