### Title
`LRTDepositPool.getAssetCurrentLimit()` Does Not Account for rsETH Daily Mint Cap, Returning Misleading Deposit Headroom - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getAssetCurrentLimit()` is the canonical on-chain view function that integrators and off-chain tooling use to determine how much of a given asset can still be deposited. It only checks the per-asset `depositLimitByAsset` cap stored in `LRTConfig`, but completely ignores the independent `maxMintAmountPerDay` daily mint cap enforced inside `RSETH.mint()`. As a result, the function can return a large positive value while any actual deposit call would immediately revert with `DailyMintLimitExceeded`, because the rsETH daily quota is already exhausted.

---

### Finding Description

`LRTDepositPool.getAssetCurrentLimit()` is defined as:

```solidity
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
}
``` [1](#0-0) 

The deposit execution path is:

1. `depositETH()` / `depositAsset()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` (checks `depositLimitByAsset`) → `_mintRsETH()` → `RSETH.mint()`. [2](#0-1) 

2. Inside `RSETH.mint()`, the `checkDailyMintLimit` modifier enforces a completely separate cap:

```solidity
if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
    revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
}
``` [3](#0-2) 

`RSETH` even exposes a dedicated view function for the remaining daily mintable amount: [4](#0-3) 

`getAssetCurrentLimit()` never consults this value. Consequently, when the daily rsETH quota is exhausted, `getAssetCurrentLimit()` still reports the full remaining per-asset headroom (potentially millions of dollars worth of ETH/LSTs), while every deposit call will revert.

---

### Impact Explanation

Any integrator — smart contract router, aggregator, or off-chain keeper — that calls `getAssetCurrentLimit()` to decide whether and how much to deposit will receive a materially incorrect answer. The contract fails to deliver the promised return (accurate deposit headroom), but no funds are permanently lost because the deposit simply reverts. This maps to the allowed impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

`maxMintAmountPerDay` is an active, configurable operational control on `RSETH`. Once the daily quota is consumed (e.g., during high-demand periods or after a large institutional deposit), the discrepancy is live for the remainder of the 24-hour window. Any integrator polling `getAssetCurrentLimit()` during that window will be misled. The likelihood is **Medium** — the condition is routine and predictable.

---

### Recommendation

`getAssetCurrentLimit()` should also account for the rsETH daily mint headroom. For example:

```solidity
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    uint256 assetHeadroom = lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;

    // Also cap by remaining rsETH daily mint quota (converted to asset units)
    address rsethToken = lrtConfig.rsETH();
    uint256 rsethHeadroom = IRSETH(rsethToken).getRemainingMintableAmount();
    uint256 rsethHeadroomInAsset = convertRsETHToAsset(asset, rsethHeadroom); // via oracle

    return assetHeadroom < rsethHeadroomInAsset ? assetHeadroom : rsethHeadroomInAsset;
}
```

---

### Proof of Concept

1. Assume `depositLimitByAsset[stETH] = 10_000e18` and `getTotalAssetDeposits(stETH) = 1_000e18`. `getAssetCurrentLimit(stETH)` returns `9_000e18`.
2. Earlier in the same 24-hour window, a large deposit already consumed the full `maxMintAmountPerDay` rsETH quota. `RSETH.getRemainingMintableAmount()` returns `0`.
3. An integrator reads `getAssetCurrentLimit(stETH) == 9_000e18` and submits a deposit of `100e18 stETH`.
4. The call reaches `RSETH.mint()`, hits `checkDailyMintLimit`, and reverts with `DailyMintLimitExceeded`.
5. The integrator's transaction fails despite `getAssetCurrentLimit()` having indicated ample capacity. [5](#0-4) [6](#0-5)

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

**File:** contracts/RSETH.sol (L269-272)
```text
        uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days) ? 0 : currentPeriodMintedAmount;

        return maxMintAmountPerDay > effectiveDailyMintAmount ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
    }
```
