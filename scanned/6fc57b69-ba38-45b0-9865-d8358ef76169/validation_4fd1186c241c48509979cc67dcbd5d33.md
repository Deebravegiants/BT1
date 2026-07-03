### Title
`LRTDepositPool::getAssetCurrentLimit()` Does Not Account for `RSETH` Daily Mint Limit, Causing Deposit DoS — (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool::getAssetCurrentLimit()` returns the remaining asset deposit capacity based solely on the per-asset deposit cap (`lrtConfig.depositLimitByAsset(asset)`). It does not account for the separate daily rsETH mint limit enforced inside `RSETH::mint()` via the `checkDailyMintLimit` modifier. When a user or integrator queries `getAssetCurrentLimit()` and submits a deposit for that amount, the transaction can revert with `DailyMintLimitExceeded` even though the asset-level limit has not been reached.

---

### Finding Description

`LRTDepositPool::depositAsset()` and `depositETH()` both call `_beforeDeposit()`, which validates the deposit against the per-asset cap: [1](#0-0) 

```solidity
function _beforeDeposit(...) private view returns (uint256 rsethAmountToMint) {
    if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
        revert MaximumDepositLimitReached();
    }
    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    ...
}
```

After passing this check, `_mintRsETH()` is called: [2](#0-1) 

```solidity
function _mintRsETH(uint256 rsethAmountToMint) private {
    address rsethToken = lrtConfig.rsETH();
    IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
}
```

`RSETH::mint()` enforces a **separate** daily mint limit: [3](#0-2) 

```solidity
modifier checkDailyMintLimit(uint256 amount) {
    ...
    if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
        revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
    }
    currentPeriodMintedAmount += amount;
    _;
}
```

The public view function `getAssetCurrentLimit()` (declared in the interface) only reflects the asset-level cap: [4](#0-3) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    ...
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

It never consults `RSETH::remainingDailyMintLimit()`: [5](#0-4) 

So when `maxMintAmountPerDay` is set and `currentPeriodMintedAmount` is close to that cap, `getAssetCurrentLimit()` returns a non-zero value, but any deposit using that value will revert inside `RSETH::mint()`.

---

### Impact Explanation

Users and integrators who call `getAssetCurrentLimit()` to determine the maximum safe deposit amount receive an inflated value. Submitting a deposit for that amount causes a revert at `RSETH::mint()`, wasting gas and making the deposit impossible until the next daily period resets. This is a **temporary DoS of deposits** — the contract fails to deliver the deposit it advertises as available.

**Severity: Low** — Contract fails to deliver promised returns, but no funds are lost.

---

### Likelihood Explanation

Requires `maxMintAmountPerDay` to be configured (non-zero) in `RSETH` and the current period's minted amount to be close to that cap while the per-asset deposit limit still has remaining capacity. Both limits are independently configurable, making this a realistic operational state, especially during high-volume deposit periods.

---

### Recommendation

`getAssetCurrentLimit()` (and `_beforeDeposit`) should also check the remaining rsETH daily mint capacity and cap the returnable/acceptable deposit amount accordingly:

```solidity
function getAssetCurrentLimit(address asset) external view returns (uint256) {
    uint256 assetLimit = lrtConfig.depositLimitByAsset(asset) - getTotalAssetDeposits(asset);
    uint256 rsethDailyRemaining = IRSETH(lrtConfig.rsETH()).remainingDailyMintLimit();
    // Convert rsETH remaining to asset units via oracle, then take the minimum
    uint256 assetEquivalentOfRsethLimit = convertRsETHToAsset(rsethDailyRemaining, asset);
    return assetLimit < assetEquivalentOfRsethLimit ? assetLimit : assetEquivalentOfRsethLimit;
}
```

---

### Proof of Concept

1. `maxMintAmountPerDay` in `RSETH` is set to `1000e18`. `currentPeriodMintedAmount` is `990e18` (10 rsETH remaining).
2. The per-asset deposit limit for stETH still has `500e18` stETH of capacity.
3. A user calls `getAssetCurrentLimit(stETH)` → returns `500e18` (ignores rsETH daily limit).
4. User calls `depositAsset(stETH, 500e18, ...)`.
5. `_beforeDeposit` passes (asset limit not exceeded).
6. `_mintRsETH(rsethAmountToMint)` calls `RSETH.mint()`.
7. `checkDailyMintLimit` reverts: `990e18 + rsethAmountToMint > 1000e18`.
8. Deposit fails despite `getAssetCurrentLimit()` indicating it was safe. [3](#0-2) [6](#0-5)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
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

**File:** contracts/RSETH.sol (L265-272)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        if (maxMintAmountPerDay == 0) return 0;

        // If we're on a new day but no mint has occurred yet, treat currentPeriodMintedAmount as 0
        uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days) ? 0 : currentPeriodMintedAmount;

        return maxMintAmountPerDay > effectiveDailyMintAmount ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
    }
```
