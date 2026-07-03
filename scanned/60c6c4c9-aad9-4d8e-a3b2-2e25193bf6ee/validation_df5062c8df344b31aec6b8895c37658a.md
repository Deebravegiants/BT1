### Title
`updateAssetDepositLimit()` Accepts Zero Value, Permanently Blocking All ERC20 Asset Deposits - (File: contracts/LRTConfig.sol)

### Summary
`LRTConfig.updateAssetDepositLimit()` sets `depositLimitByAsset[asset]` without a zero-value guard. If the MANAGER role sets the limit to zero (by mistake or to "disable" deposits), every subsequent `depositAsset()` call for that asset reverts unconditionally, freezing new deposits until the limit is corrected.

### Finding Description
`_addNewSupportedAsset()` correctly rejects a zero deposit limit: [1](#0-0) 

But the update path `updateAssetDepositLimit()` has no equivalent guard: [2](#0-1) 

`depositLimitByAsset[asset]` is then consumed by `_checkIfDepositAmountExceedesCurrentLimit()` in `LRTDepositPool`: [3](#0-2) 

For any ERC20 asset, the check is `totalAssetDeposits + amount > depositLimitByAsset[asset]`. When the limit is `0`, this expression evaluates to `true` for every non-zero `amount` (the zero-amount case is already rejected earlier), so `_beforeDeposit` always reverts with `MaximumDepositLimitReached`: [4](#0-3) 

### Impact Explanation
**Medium — Temporary freezing of funds.**  
All `depositAsset()` calls for the affected asset revert until the MANAGER issues a corrective `updateAssetDepositLimit()` call with a non-zero value. No funds already in the protocol are lost, but new deposits are completely blocked for the duration of the misconfiguration.

### Likelihood Explanation
**Low.** The MANAGER role must call `updateAssetDepositLimit(asset, 0)`. This can happen by mistake (e.g., intending to "disable" the limit by passing `0`, analogous to how `removeSupportedAsset` sets the limit to `0` internally) or through a fat-finger error. The inconsistency with `_addNewSupportedAsset`'s explicit zero-check makes the mistake more plausible.

### Recommendation
Add a zero-value guard to `updateAssetDepositLimit()`, mirroring the check already present in `_addNewSupportedAsset()`:

```solidity
function updateAssetDepositLimit(address asset, uint256 depositLimit)
    external
    onlyRole(LRTConstants.MANAGER)
    onlySupportedAsset(asset)
{
    if (depositLimit == 0) revert InvalidDepositLimit();
    depositLimitByAsset[asset] = depositLimit;
    emit AssetDepositLimitUpdate(asset, depositLimit);
}
```

### Proof of Concept
1. MANAGER calls `LRTConfig.updateAssetDepositLimit(stETH, 0)`.
2. `depositLimitByAsset[stETH]` is now `0`.
3. Any user calls `LRTDepositPool.depositAsset(stETH, 1 ether, 0, "")`.
4. `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit(stETH, 1e18)` → evaluates `totalAssetDeposits + 1e18 > 0` → `true`.
5. Transaction reverts with `MaximumDepositLimitReached`. All stETH deposits are blocked. [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTConfig.sol (L108-110)
```text
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
```

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
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
