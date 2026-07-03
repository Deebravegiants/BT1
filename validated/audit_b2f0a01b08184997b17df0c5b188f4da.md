### Title
`LRTDepositPool.getAssetCurrentLimit()` Does Not Account for `RSETH.maxMintAmountPerDay`, Returning an Inflated Deposit Capacity - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getAssetCurrentLimit()` calculates the remaining deposit capacity solely against the per-asset deposit cap stored in `LRTConfig.depositLimitByAsset`. It does not account for the independent daily rsETH mint cap (`maxMintAmountPerDay`) enforced inside `RSETH.checkDailyMintLimit`. When the daily rsETH mint limit is exhausted, `getAssetCurrentLimit()` still returns a non-zero value, causing any deposit attempt that relies on this value to revert at `RSETH.mint()`.

---

### Finding Description

`LRTDepositPool.getAssetCurrentLimit()` is a public view function exposed in the `ILRTDepositPool` interface. It is the canonical way for users and integrators to determine how much of a given asset can still be deposited:

```solidity
// contracts/LRTDepositPool.sol:402-409
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
}
```

The function only checks the per-asset deposit cap from `LRTConfig`. It is completely unaware of the second, independent limit: the daily rsETH mint cap enforced by `RSETH.checkDailyMintLimit`:

```solidity
// contracts/RSETH.sol:42-56
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

The deposit execution path is:

1. User calls `depositETH()` or `depositAsset()`.
2. `_beforeDeposit()` calls `_checkIfDepositAmountExceedesCurrentLimit()` — checks only `lrtConfig.depositLimitByAsset`.
3. `_mintRsETH()` calls `IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)`.
4. `RSETH.mint()` applies `checkDailyMintLimit(amount)` — **this is the gate that `getAssetCurrentLimit()` never consults**.

```solidity
// contracts/LRTDepositPool.sol:686-690
function _mintRsETH(uint256 rsethAmountToMint) private {
    address rsethToken = lrtConfig.rsETH();
    IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
}
```

`RSETH` also exposes `remainingDailyMintLimit()` as a separate view function, confirming the daily cap is a first-class production constraint. `getAssetCurrentLimit()` never reads it.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

When `maxMintAmountPerDay` is set and the daily quota is exhausted, `getAssetCurrentLimit()` returns a positive value even though no deposit can succeed. Any user or on-chain integrator that reads `getAssetCurrentLimit()` to size a deposit will have their transaction revert with `DailyMintLimitExceeded`. For ETH deposits the native value is returned on revert; for LST deposits the `safeTransferFrom` has already executed before `_mintRsETH` is called, but the entire transaction reverts atomically, so no tokens are permanently lost. The harm is failed transactions and misleading protocol state reporting.

---

### Likelihood Explanation

**Medium.** `maxMintAmountPerDay` has a dedicated setter (`setMaxMintAmountPerDay`), a dedicated view (`remainingDailyMintLimit()`), and a dedicated reset timestamp getter (`getNextDailyLimitResetTimestamp()`), all indicating it is an active production control. Any depositor who queries `getAssetCurrentLimit()` when the per-asset cap still has headroom but the daily rsETH mint quota is exhausted will receive an inflated value and experience a revert. This is a normal operating condition at the end of a high-volume day.

---

### Recommendation

`getAssetCurrentLimit()` should also factor in the remaining rsETH daily mint capacity. The rsETH amount that can still be minted today (`RSETH.remainingDailyMintLimit()`) should be converted back to asset units using the current exchange rate (`LRTOracle.getAssetPrice` / `rsETHPrice`) and the result should be the minimum of the two limits:

```solidity
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    // Existing per-asset cap check
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) return 0;
    uint256 assetCapRemaining = lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;

    // Additional: daily rsETH mint cap check
    address rsethToken = lrtConfig.rsETH();
    uint256 rsethDailyRemaining = IRSETH(rsethToken).remainingDailyMintLimit();
    if (rsethDailyRemaining == 0) return 0;

    // Convert rsETH remaining to asset units
    address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
    ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);
    uint256 assetFromDailyLimit = (rsethDailyRemaining * lrtOracle.rsETHPrice()) / lrtOracle.getAssetPrice(asset);

    return assetCapRemaining < assetFromDailyLimit ? assetCapRemaining : assetFromDailyLimit;
}
```

---

### Proof of Concept

1. Admin sets `maxMintAmountPerDay = 1000 ether` on `RSETH`.
2. During the day, 999 ether worth of rsETH is minted; `RSETH.remainingDailyMintLimit()` returns `1 ether`.
3. The per-asset deposit cap for stETH still has `500 ether` of headroom.
4. A user calls `LRTDepositPool.getAssetCurrentLimit(stETH)` → returns `500 ether`.
5. The user calls `depositAsset(stETH, 2 ether, ...)` (within the asset cap, but exceeds the daily rsETH quota).
6. `_beforeDeposit` passes (asset cap not exceeded).
7. `_mintRsETH` calls `RSETH.mint(user, rsethAmount)`.
8. `checkDailyMintLimit` reverts with `DailyMintLimitExceeded(currentPeriodMintedAmount + rsethAmount, maxMintAmountPerDay)`.
9. The transaction reverts despite `getAssetCurrentLimit()` having indicated capacity was available. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** contracts/RSETH.sol (L263-272)
```text
    /// @notice Gets the remaining daily minting limit
    /// @return uint256 The remaining daily minting limit
    function remainingDailyMintLimit() external view returns (uint256) {
        if (maxMintAmountPerDay == 0) return 0;

        // If we're on a new day but no mint has occurred yet, treat currentPeriodMintedAmount as 0
        uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days) ? 0 : currentPeriodMintedAmount;

        return maxMintAmountPerDay > effectiveDailyMintAmount ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
    }
```

**File:** contracts/interfaces/ILRTDepositPool.sol (L60-60)
```text
    function getAssetCurrentLimit(address asset) external view returns (uint256);
```
