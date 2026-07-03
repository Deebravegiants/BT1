### Title
`LRTConfig.updateAssetStrategy()` Does Not Verify New Strategy's Underlying Token Matches the Asset - (File: contracts/LRTConfig.sol)

### Summary

`LRTConfig.updateAssetStrategy()` maps an `asset` address to an EigenLayer `strategy` address without verifying that `IStrategy(strategy).underlyingToken() == asset`. If the admin accidentally assigns a strategy whose underlying token differs from the asset (e.g., mapping stETH to the ethX EigenLayer strategy), subsequent calls to `NodeDelegator.depositAssetIntoStrategy()` will revert, assets will be stranded in the NDC, and `NodeDelegatorHelper.getAssetBalance()` will return incorrect values for that asset, corrupting the oracle's TVL accounting.

### Finding Description

`LRTConfig.updateAssetStrategy()` performs three checks before writing `assetStrategy[asset] = strategy`:

1. Strategy address is non-zero
2. Strategy is not already set to the same address
3. If a prior strategy exists, no NDC currently holds shares in it [1](#0-0) 

What it does **not** check is whether `IStrategy(strategy).underlyingToken()` equals `asset`. The `underlyingToken()` getter is part of the `IStrategy` interface already imported by `LRTConfig.sol`: [2](#0-1) 

When `depositAssetIntoStrategy(asset)` is later called on a `NodeDelegator`, it reads the (wrong) strategy from config and passes the asset token directly to EigenLayer's `StrategyManager`: [3](#0-2) 

EigenLayer's `StrategyBase.deposit` enforces `token == underlyingToken` and reverts with `OnlyUnderlyingToken`, so the asset remains as a raw ERC-20 balance in the NDC rather than being restaked.

Additionally, `NodeDelegatorHelper.getAssetBalance()` queries the (wrong) strategy for the NDC's shares: [4](#0-3) 

Because the NDC has zero shares in the wrong strategy, this returns 0, causing `LRTOracle._getTotalEthInProtocol()` to undercount the asset's TVL and compute a deflated rsETH price. [5](#0-4) 

### Impact Explanation

- `depositAssetIntoStrategy` reverts for the misconfigured asset; assets accumulate in the NDC and cannot be restaked into EigenLayer.
- `getAssetBalance` returns 0 for the NDC's holdings of that asset, causing the oracle to undercount TVL and produce a deflated rsETH price.
- The protocol fails to deliver the promised EigenLayer restaking yield for the affected asset until the admin corrects the mapping.
- Funds are not permanently lost (the admin can call `updateAssetStrategy` again with the correct strategy, and assets can be transferred back via `transferBackToLRTDepositPool`), but the protocol does not deliver its promised returns during the misconfiguration window.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation

The protocol supports multiple assets (stETH, ethX, and any future additions via `addNewSupportedAsset`), each with a distinct EigenLayer strategy. As the number of supported assets grows, the probability of an admin accidentally supplying the wrong strategy address increases. The mistake requires no attacker — only an honest admin error during routine strategy management.

### Recommendation

Add a token-match check inside `updateAssetStrategy()` before writing the new strategy:

```solidity
require(
    IStrategy(strategy).underlyingToken() == IERC20(asset),
    "Strategy underlying token mismatch"
);
```

This mirrors the fix recommended in the original report (`require(_baseToken == _newStrategy.getBaseToken())`) and uses the `underlyingToken()` getter already present in the `IStrategy` interface. [6](#0-5) 

### Proof of Concept

1. Protocol has two supported assets: `stETH` (mapped to `stETHStrategy`) and `ethX` (mapped to `ethXStrategy`).
2. Admin calls `updateAssetStrategy(stETH, ethXStrategy)` by mistake (e.g., copy-paste error).
3. No revert occurs — the function only checks non-zero address and absence of existing NDC funds.
4. Operator calls `NodeDelegator.depositAssetIntoStrategy(stETH)`.
5. `NodeDelegator` fetches `strategy = lrtConfig.assetStrategy(stETH)` → `ethXStrategy`.
6. Calls `IStrategyManager.depositIntoStrategy(ethXStrategy, stETH_token, balance)`.
7. EigenLayer reverts: `ethXStrategy.deposit(stETH_token, amount)` fails with `OnlyUnderlyingToken`.
8. stETH remains in the NDC; `getAssetBalance(stETH)` queries `ethXStrategy.userUnderlyingView(NDC)` → returns 0.
9. `LRTOracle._getTotalEthInProtocol()` undercounts stETH TVL → rsETH price is deflated. [1](#0-0) [7](#0-6) [4](#0-3)

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

**File:** contracts/external/eigenlayer/interfaces/IStrategy.sol (L128-130)
```text
    /// @notice The underlying token for shares in this Strategy
    function underlyingToken() external view returns (IERC20);

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

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
