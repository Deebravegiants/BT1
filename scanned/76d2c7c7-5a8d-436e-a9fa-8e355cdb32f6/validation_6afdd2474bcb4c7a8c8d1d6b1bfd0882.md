### Title
`updateAssetDepositLimit` Can Be Set Below Current Total Deposits, Temporarily Blocking All Deposits - (File: contracts/LRTConfig.sol)

### Summary
`updateAssetDepositLimit()` in `LRTConfig.sol` sets `depositLimitByAsset[asset]` to an arbitrary new value with no on-chain check that the new limit is ≥ the current total deposits already held in the protocol. The manager is expected to call `getTotalAssetDeposits(asset)` off-chain before reducing the limit, but a user deposit between that off-chain read and the on-chain setter call can cause the limit to land below the live total, permanently blocking all further deposits for that asset until the manager intervenes again.

### Finding Description
`updateAssetDepositLimit` writes directly to `depositLimitByAsset[asset]` with no guard:

```solidity
// LRTConfig.sol L123-133
function updateAssetDepositLimit(
    address asset,
    uint256 depositLimit
)
    external
    onlyRole(LRTConstants.MANAGER)
    onlySupportedAsset(asset)
{
    depositLimitByAsset[asset] = depositLimit;          // no check vs. current deposits
    emit AssetDepositLimitUpdate(asset, depositLimit);
}
```

Every deposit path in `LRTDepositPool` passes through `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// LRTDepositPool.sol L676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

If `depositLimitByAsset[asset]` is set below the live `totalAssetDeposits`, the condition is always `true` for every non-zero deposit amount, and every call to `depositAsset` / `depositETH` reverts with `MaximumDepositLimitReached`. The public view `getAssetCurrentLimit` also returns `0`, misleading integrators and front-ends.

The analog to the external report's manual step is that the manager is expected to read `getTotalAssetDeposits(asset)` off-chain before choosing the new limit. A user who deposits in the window between that read and the on-chain `updateAssetDepositLimit` call causes the new limit to be set below the live total, triggering the DoS.

### Impact Explanation
All new deposits for the affected asset are blocked until the manager calls `updateAssetDepositLimit` again with a corrected value. Existing depositor funds are safe and withdrawable, but the protocol fails to accept any new deposits for that asset during the window. This maps to **Low — contract fails to deliver promised returns, but doesn't lose value**, because no funds are lost or frozen; only the deposit entry point is broken.

### Likelihood Explanation
The manager must be in the process of reducing the deposit limit (a routine operational action). A concurrent innocent user deposit during the off-chain-read → on-chain-write window is sufficient to trigger the condition; no adversarial front-running is required. The window can span multiple blocks given the manual, multi-step nature of the operation, making accidental triggering plausible.

### Recommendation
Add an on-chain guard in `updateAssetDepositLimit` that enforces the new limit is at least equal to the current total deposits:

```solidity
function updateAssetDepositLimit(address asset, uint256 depositLimit)
    external
    onlyRole(LRTConstants.MANAGER)
    onlySupportedAsset(asset)
{
    address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);
    require(
        depositLimit >= ILRTDepositPool(depositPool).getTotalAssetDeposits(asset),
        "ERR_LIMIT_BELOW_CURRENT_DEPOSITS"
    );
    depositLimitByAsset[asset] = depositLimit;
    emit AssetDepositLimitUpdate(asset, depositLimit);
}
```

This is the direct analog to the mitigation recommended in the external report (`require(_perTokenWalletCap <= getMaxCommunityLpPositon(_token))`).

### Proof of Concept
1. Current `totalAssetDeposits(stETH)` = 90,000 stETH. Manager reads this off-chain and decides to set the new limit to 95,000 stETH.
2. Before the manager's transaction lands, an innocent user deposits 6,000 stETH, bringing `totalAssetDeposits` to 96,000 stETH.
3. Manager's `updateAssetDepositLimit(stETH, 95_000 ether)` executes. Now `depositLimitByAsset[stETH]` = 95,000 < 96,000 = `totalAssetDeposits`.
4. Every subsequent call to `depositAsset(stETH, ...)` hits `_checkIfDepositAmountExceedesCurrentLimit` → `96000 + amount > 95000` → `true` → reverts with `MaximumDepositLimitReached`.
5. `getAssetCurrentLimit(stETH)` returns `0`, breaking any integrator or UI relying on it.
6. All stETH deposits are frozen until the manager calls `updateAssetDepositLimit` again with a value ≥ 96,000 stETH.

**Root cause:** [1](#0-0) 

**Deposit gate that enforces the limit:** [2](#0-1) 

**View function that returns 0 when limit is breached:** [3](#0-2) 

**Deposit revert path:** [4](#0-3)

### Citations

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
