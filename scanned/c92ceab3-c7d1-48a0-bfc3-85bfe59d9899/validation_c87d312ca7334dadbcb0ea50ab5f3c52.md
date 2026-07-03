### Title
Unbounded Nested-Loop Gas Consumption in `updateRSETHPrice()` Can Permanently Stale the rsETH Price — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function whose gas cost scales multiplicatively with the number of supported assets, node delegators, EigenLayer queued withdrawals per NDC, and strategies per withdrawal. As the protocol grows through normal operation, this function can exceed the block gas limit, permanently preventing rsETH price updates and disabling the protocol's downside-protection pause mechanism.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no role restriction, meaning any external caller can invoke it. [1](#0-0) 

It delegates to `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`: [2](#0-1) 

`_getTotalEthInProtocol()` iterates over every entry in `supportedAssets` and for each calls `ILRTDepositPool.getTotalAssetDeposits(asset)`.

`getTotalAssetDeposits()` calls `getAssetDistributionData()`: [3](#0-2) 

`getAssetDistributionData()` loops over every entry in `nodeDelegatorQueue` and for each NDC calls `INodeDelegator.getAssetUnstaking(asset)`: [4](#0-3) 

`getAssetUnstaking()` fetches **all** queued EigenLayer withdrawals for the NDC and then runs a **nested loop** over each withdrawal's strategy array, making external calls to `strategy.underlyingToken()` and `strategy.sharesToUnderlyingView()` inside the inner loop: [5](#0-4) 

The total gas cost therefore scales as:

```
supportedAssets.length
  × nodeDelegatorQueue.length
    × queuedWithdrawals.length (per NDC)
      × withdrawal.strategies.length
```

Each inner iteration involves multiple external SLOAD-heavy calls to EigenLayer contracts. The team is explicitly aware of this concern — `LRTUnstakingVault` caps `maxUncompletedWithdrawalCount` at 80 with the comment: [6](#0-5) 

However, this cap is a **global** protocol-side counter, not a per-NDC EigenLayer enforcement. Forced undelegations by EigenLayer operators can add additional queued withdrawals beyond the protocol's tracked count (the comment itself acknowledges up to 15 extra from forced undelegations). Furthermore, the cap does not account for growth in the number of supported assets or NDCs.

---

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit, the rsETH price stored in `rsETHPrice` becomes permanently stale. Consequences:

1. **Stale price used for minting**: `getRsETHAmountToMint()` reads `lrtOracle.rsETHPrice()` directly, so new depositors receive rsETH at an incorrect rate.
2. **Stale price used for withdrawals**: `getExpectedAssetAmount()` in `LRTWithdrawalManager` reads `lrtOracle.rsETHPrice()`, causing incorrect withdrawal amounts.
3. **Downside protection disabled**: `_updateRsETHPrice()` contains the logic that pauses the protocol when the price drops too far below its peak. If the function is uncallable, this safety mechanism never triggers.

Impact classification: **Medium — Unbounded gas consumption / Temporary (potentially permanent) freezing of the price-update mechanism with downstream effects on minting and withdrawal accuracy.**

---

### Likelihood Explanation

The gas cost grows through entirely normal protocol operation: adding more supported LSTs, deploying more `NodeDelegator` contracts, and operators queuing EigenLayer withdrawals. No malicious actor is required. The team's own comment acknowledges the gas ceiling is near the current operational parameters (80 tracked + up to 15 forced = 95 queued withdrawals per NDC). As the protocol scales, the ceiling will be breached.

---

### Recommendation

1. **Cache `getAssetUnstaking` results off-chain** and push them on-chain via a privileged setter, rather than recomputing them live inside `updateRSETHPrice()`.
2. **Decouple TVL accounting from price updates**: store per-NDC asset balances in a mapping updated lazily by operators, and have `_getTotalEthInProtocol()` read from that mapping instead of making live external calls.
3. **Enforce per-NDC withdrawal caps** at the EigenLayer level (not just a global protocol counter) to bound the inner loop.
4. **Benchmark gas cost** at maximum expected `supportedAssets × NDC × withdrawal × strategy` cardinality and enforce hard limits that keep the function safely below the block gas limit.

---

### Proof of Concept

Call trace that demonstrates the nested unbounded iteration:

```
updateRSETHPrice()                          [LRTOracle.sol:87]  — public, no role check
  └─ _updateRsETHPrice()                   [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()         [LRTOracle.sol:331]
            └─ for each asset in supportedAssets:          [LRTOracle.sol:336]
                 └─ getTotalAssetDeposits(asset)           [LRTDepositPool.sol:385]
                      └─ getAssetDistributionData(asset)   [LRTDepositPool.sol:426]
                           └─ for each NDC in nodeDelegatorQueue:   [LRTDepositPool.sol:447]
                                └─ getAssetUnstaking(asset)         [NodeDelegator.sol:405]
                                     └─ getQueuedWithdrawals(NDC)   [external EigenLayer call]
                                          └─ for each withdrawal:   [NodeDelegator.sol:409]
                                               └─ for each strategy: [NodeDelegator.sol:412]
                                                    └─ strategy.underlyingToken()        [external]
                                                    └─ strategy.sharesToUnderlyingView() [external]
```

With 5 supported assets, 10 NDCs, 80 queued withdrawals per NDC, and 3 strategies per withdrawal, the inner body executes **12,000 times**, each involving multiple external calls. At ~5,000 gas per external call, this alone approaches 60M gas — well above Ethereum's 30M block gas limit.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
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

**File:** contracts/LRTUnstakingVault.sol (L151-155)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
```
