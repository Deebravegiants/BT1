Audit Report

## Title
Nested Per-Asset Iteration Over EigenLayer Queued Withdrawals Causes Multiplicative Gas Growth in `updateRSETHPrice()` and `depositAsset()`/`depositETH()` — (File: `contracts/NodeDelegator.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

## Summary
`NodeDelegator.getAssetUnstaking()` calls `DelegationManager.getQueuedWithdrawals()` and iterates over all returned withdrawals on every invocation. This function is called once per NDC inside `LRTDepositPool.getAssetDistributionData()`, which is itself called once per supported asset inside `LRTOracle._getTotalEthInProtocol()`. The result is that the total number of external EigenLayer calls scales as `N_assets × N_NDCs` and total inner iterations scale as `N_assets × N_NDCs × N_withdrawals × N_strategies`. Both the public `updateRSETHPrice()` and every user `depositAsset()`/`depositETH()` call traverse this path, with no caching of withdrawal data across assets.

## Finding Description
**Root cause — `NodeDelegator.getAssetUnstaking()`:** [1](#0-0) 

Every call fetches the full `getQueuedWithdrawals(address(this))` result from EigenLayer and iterates over every withdrawal and every strategy within it, regardless of which asset is being queried. There is no caching; the same full withdrawal list is re-fetched for each asset.

**First nesting layer — `LRTDepositPool.getAssetDistributionData()`:** [2](#0-1) 

For a single asset, this loops over all NDCs and calls `getAssetUnstaking(asset)` on each, producing `N_NDCs` external calls to EigenLayer.

**Second nesting layer — `LRTOracle._getTotalEthInProtocol()`:** [3](#0-2) 

This loops over every supported asset and calls `getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` for each, multiplying the NDC loop by `N_assets`. Total external calls: `N_assets × N_NDCs`. Total inner iterations: `N_assets × N_NDCs × N_withdrawals × N_strategies`.

**Public entry point — `LRTOracle.updateRSETHPrice()`:** [4](#0-3) 

`public whenNotPaused` — callable by any address with no access restriction.

**User deposit entry point:** [5](#0-4) 

Every `depositAsset()`/`depositETH()` call invokes `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()`, triggering the full NDC loop and `getAssetUnstaking()` for the deposited asset.

**Developer acknowledgment of the gas concern:** [6](#0-5) 

The comment explicitly states "120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price," confirming the developers are aware that beyond a certain withdrawal count the function becomes uncallable. The cap is set to 80 to leave a buffer, but this cap applies per-NDC and does not account for the multiplicative effect of iterating per asset.

**Why existing guards are insufficient:**
The `maxUncompletedWithdrawalCount ≤ 80` cap limits withdrawals per NDC, and `maxNodeDelegatorLimit = 10` caps NDCs. However, there is no cap on `supportedAssetList` length. As more assets are added, the same withdrawal data for each NDC is fetched redundantly once per asset. With 5 assets, 10 NDCs, and 80 withdrawals each, the path through `updateRSETHPrice()` produces 50 external calls and up to 8,000 inner iterations — all within a single transaction callable by any user.

## Impact Explanation
**Medium — Unbounded gas consumption / Temporary freezing of funds.**

As the protocol scales (more supported assets added, more concurrent EigenLayer unstaking operations), the gas cost of `updateRSETHPrice()` and `depositAsset()`/`depositETH()` grows multiplicatively without any single cap preventing the combined product from exceeding the block gas limit. If this occurs: (1) `updateRSETHPrice()` becomes uncallable, freezing the rsETH price at a stale value; (2) `depositAsset()`/`depositETH()` revert on every call, temporarily freezing user deposits into the protocol.

## Likelihood Explanation
**Medium.** No attacker action is required — the gas growth is a natural consequence of protocol scaling (adding assets, deploying NDCs, accumulating EigenLayer withdrawals). Any user can call `updateRSETHPrice()` to observe or force the failure. The developers' own comment confirms awareness that the function has a practical gas ceiling, and the existing caps do not fully bound the multiplicative cross-asset × cross-NDC product.

## Recommendation
1. **Cache `getQueuedWithdrawals()` per NDC per transaction** rather than calling it once per asset per NDC. A single call per NDC can serve all assets in a single pass.
2. **Maintain a running `totalUnstaking` counter per asset per NDC** (incremented on `initiateUnstaking`, decremented on `completeUnstaking`), eliminating the need to iterate over EigenLayer's withdrawal queue at read time entirely.
3. **Apply a hard cap on `supportedAssetList` length** in addition to the existing NDC and withdrawal caps, to bound the multiplicative factor.

## Proof of Concept
Call chain for `updateRSETHPrice()` (callable by any user, no preconditions):

```
LRTOracle.updateRSETHPrice()                          // public, no access control
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()                    // loops over N_assets supported assets
            └─ ILRTDepositPool.getTotalAssetDeposits(asset)
                 └─ getAssetDistributionData(asset)   // loops over N_ndcs NDCs
                      └─ INodeDelegator.getAssetUnstaking(asset)
                           └─ DelegationManager.getQueuedWithdrawals(ndc)
                                                      // external call, returns up to 80 withdrawals
                                └─ for each withdrawal (N_withdrawals):
                                     for each strategy (N_strategies): ...
```

**Foundry fork test plan:**
1. Fork Ethereum mainnet with the deployed contracts.
2. Add 5 supported assets via `LRTConfig.addNewSupportedAsset()` (admin action, sets up realistic state).
3. Deploy 10 NDCs and register them in `nodeDelegatorQueue`.
4. Initiate 80 EigenLayer withdrawals across each NDC (or mock `DelegationManager.getQueuedWithdrawals` to return 80 entries).
5. Call `LRTOracle.updateRSETHPrice()` from an unprivileged EOA and measure gas with `vm.expectCall` counting external calls and `gasleft()` before/after.
6. Observe that gas consumption approaches or exceeds the block gas limit (30M), confirming the transaction reverts or becomes economically unviable.

### Citations

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTUnstakingVault.sol (L151-153)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
```
