### Title
Missing `strategy.underlyingToken() == asset` Validation in `updateAssetStrategy` — (`contracts/LRTConfig.sol`)

### Summary

`LRTConfig.updateAssetStrategy()` maps an asset address to an EigenLayer strategy address but never verifies that `IStrategy(strategy).underlyingToken() == asset`. If a mismatched strategy is set (by admin mistake), `NodeDelegator.depositAssetIntoStrategy()` will revert on every call (EigenLayer enforces the token-strategy match internally), permanently preventing the asset from being restaked into EigenLayer and causing the asset to remain idle in the NodeDelegator.

### Finding Description

`LRTConfig.updateAssetStrategy()` performs two checks before writing the mapping: it ensures the strategy address is non-zero and that the strategy is not already set for the asset. It does **not** check that the strategy's underlying token matches the asset being registered. [1](#0-0) 

When `NodeDelegator.depositAssetIntoStrategy(asset)` is later called, it reads the strategy from `lrtConfig.assetStrategy(asset)` and passes both the strategy and the asset token directly to EigenLayer's `StrategyManager.depositIntoStrategy()`. [2](#0-1) 

EigenLayer's `StrategyManager` enforces internally that the token passed matches the strategy's `underlyingToken()`. If they differ, the call reverts. Because the mismatch is never caught at configuration time, every subsequent `depositAssetIntoStrategy` call for that asset will revert, leaving the asset permanently idle in the NodeDelegator.

`NodeDelegatorHelper.getAssetBalance()` also blindly trusts the strategy mapping: it fetches the strategy for the given asset and calls `sharesToUnderlyingView` on it without verifying the strategy's underlying token matches the asset. [3](#0-2) 

### Impact Explanation

Assets deposited into the NodeDelegator cannot be forwarded to EigenLayer for restaking. They sit idle, earning no EigenLayer rewards. The protocol fails to deliver its core promised return (EigenLayer restaking yield) for the affected asset. TVL accounting via `IERC20(asset).balanceOf(nodeDelegatorQueue[i])` still counts the idle tokens correctly, so there is no direct fund loss or oracle manipulation — the impact is confined to yield loss.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation

`updateAssetStrategy` is callable only by `DEFAULT_ADMIN_ROLE`. The trigger is an admin configuration mistake (e.g., copy-paste error when onboarding a new LST and its corresponding EigenLayer strategy), not a compromise. Given that the protocol supports multiple LSTs each with a distinct EigenLayer strategy, the probability of a misconfiguration is non-negligible, especially during protocol expansion. No attacker action is required; the mistake alone is sufficient.

### Recommendation

Add a token-match assertion inside `updateAssetStrategy` before writing the mapping:

```solidity
function updateAssetStrategy(address asset, address strategy) external onlyRole(DEFAULT_ADMIN_ROLE) onlySupportedAsset(asset) {
    UtilLib.checkNonZeroAddress(strategy);
    if (assetStrategy[asset] == strategy) revert ValueAlreadyInUse();

    // *** ADD THIS CHECK ***
    if (IStrategy(strategy).underlyingToken() != IERC20(asset)) {
        revert StrategyAssetMismatch();
    }
    // ... existing funds check ...
    assetStrategy[asset] = strategy;
    emit AssetStrategyUpdate(asset, strategy);
}
```

This mirrors the fix applied in the referenced protocol (PR 237), where the check was added at the point of component registration rather than at the point of use.

### Proof of Concept

1. Admin calls `LRTConfig.updateAssetStrategy(stETH, wrongStrategy)` where `wrongStrategy.underlyingToken()` returns `ETH` (or any token ≠ stETH). The call succeeds — no revert.
2. Operator calls `NodeDelegator.depositAssetIntoStrategy(stETH)`. The function reads `strategy = wrongStrategy` and calls `IStrategyManager.depositIntoStrategy(wrongStrategy, IERC20(stETH), balance)`.
3. EigenLayer's `StrategyManager` checks `token == strategy.underlyingToken()` → `stETH != ETH` → **reverts**.
4. stETH tokens remain stuck in the NodeDelegator indefinitely. No EigenLayer restaking rewards accrue for stETH holders.
5. The only recovery path is a new admin call to `updateAssetStrategy` with the correct strategy, but the existing check `if (assetStrategy[asset] == strategy) revert ValueAlreadyInUse()` does not block this correction. [1](#0-0) [4](#0-3) [3](#0-2)

### Citations

**File:** contracts/LRTConfig.sol (L138-171)
```text
    function updateAssetStrategy(
        address asset,
        address strategy
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedAsset(asset)
    {
        UtilLib.checkNonZeroAddress(strategy);
        if (assetStrategy[asset] == strategy) {
            revert ValueAlreadyInUse();
        }
        // if strategy is already set, check if it has any funds
        if (assetStrategy[asset] != address(0)) {
            // get ndcs
            address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);
            address[] memory ndcs = ILRTDepositPool(depositPool).getNodeDelegatorQueue();

            uint256 length = ndcs.length;
            for (uint256 i = 0; i < length;) {
                uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
                if (ndcBalance > 0) {
                    revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
                }

                unchecked {
                    ++i;
                }
            }
        }

        assetStrategy[asset] = strategy;
        emit AssetStrategyUpdate(asset, strategy);
    }
```

**File:** contracts/NodeDelegator.sol (L92-112)
```text
    function depositAssetIntoStrategy(address asset)
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlyLRTOperator
    {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            revert StrategyIsNotSetForAsset();
        }

        IERC20 token = IERC20(asset);

        uint256 balance = token.balanceOf(address(this));

        IStrategyManager(lrtConfig.strategyManager()).depositIntoStrategy(IStrategy(strategy), token, balance);

        emit AssetDepositIntoStrategy(asset, strategy, balance);
    }
```

**File:** contracts/NodeDelegatorHelper.sol (L31-39)
```text
    function getAssetBalance(ILRTConfig lrtConfig, address asset) internal view returns (uint256) {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            return 0;
        }
        uint256 withdrawableShare = getWithdrawableShare(lrtConfig, IStrategy(strategy));

        return IStrategy(strategy).sharesToUnderlyingView(withdrawableShare);
    }
```
