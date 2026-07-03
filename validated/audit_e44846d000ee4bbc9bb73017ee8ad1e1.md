Audit Report

## Title
Unbounded Nested-Loop Gas Consumption in `getAssetUnstaking` Propagates Through Every Deposit and Withdrawal Path — (File: `contracts/NodeDelegator.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

## Summary
`NodeDelegator.getAssetUnstaking()` fetches the full list of pending EigenLayer withdrawals via `getQueuedWithdrawals()` and iterates over them with a nested loop on every call. This function is invoked once per NDC per asset inside `LRTDepositPool.getAssetDistributionData()` and `getETHDistributionData()`, which are themselves called on every user deposit (`depositETH`, `depositAsset`) and by the public `LRTOracle.updateRSETHPrice()`. As the protocol scales across supported assets, NDCs, and queued withdrawals, the cumulative gas cost grows multiplicatively and can exceed the block gas limit, permanently bricking deposits and price updates.

## Finding Description

**Root cause — `NodeDelegator.getAssetUnstaking()`:**

`getAssetUnstaking()` calls `_getDelegationManager().getQueuedWithdrawals(address(this))` unconditionally, deserializing the full withdrawal queue from EigenLayer storage, then iterates over every withdrawal and every strategy within it: [1](#0-0) 

**Propagation into `getAssetDistributionData()` — called on every deposit:**

`getAssetDistributionData()` calls `getAssetUnstaking()` once per NDC in a loop, multiplying the cost by the number of deployed NDCs: [2](#0-1) 

`getETHDistributionData()` has the identical pattern for ETH: [3](#0-2) 

**`getTotalAssetDeposits()` calls `getAssetDistributionData()`:** [4](#0-3) 

**`getAssetCurrentLimit()` calls `getTotalAssetDeposits()`**, which is invoked on every deposit via `_beforeDeposit()`: [5](#0-4) 

**Propagation into `_getTotalEthInProtocol()` — called by the public `updateRSETHPrice()`:**

`_getTotalEthInProtocol()` loops over all supported assets and calls `getTotalAssetDeposits()` for each, triggering the full NDC × withdrawal nested loop per asset: [6](#0-5) 

`updateRSETHPrice()` is public with no access control beyond `whenNotPaused`: [7](#0-6) 

**Existing mitigation is insufficient — only one dimension is bounded:**

`setMaxUncompletedWithdrawalCount()` caps queued withdrawals per NDC at 80, and the protocol's own comment acknowledges the gas ceiling concern: [8](#0-7) 

However, `supportedAssetList` has no hard cap — assets are pushed without limit: [9](#0-8) 

And `maxNodeDelegatorLimit` is admin-raiseable with no ceiling: [10](#0-9) 

**Total gas cost per call scales as:**
```
O(supportedAssets × ndcCount × queuedWithdrawals × strategiesPerWithdrawal)
```
With 5 assets, 10 NDCs, and 80 queued withdrawals each, `updateRSETHPrice()` triggers 50 separate `getQueuedWithdrawals()` calls, each deserializing up to 80 `Withdrawal` structs from EigenLayer storage. Adding more assets (a routine governance action) multiplies this cost further with no ceiling.

## Impact Explanation

When cumulative gas cost exceeds the block gas limit:
1. `depositETH()` / `depositAsset()` revert with OOG — no new deposits can be made, constituting a temporary (escalating to permanent) freezing of user funds in transit.
2. `updateRSETHPrice()` reverts — the rsETH price becomes permanently stale, disabling the price-drop circuit-breaker that auto-pauses the protocol.

**Impact: Medium — Unbounded gas consumption / Temporary freezing of funds.**

## Likelihood Explanation

No attacker action is required. The DoS emerges from ordinary protocol scaling: adding LST collateral types via governance, deploying more NDCs to scale EigenLayer restaking, and accumulating queued withdrawals during normal operations. Each legitimate growth step increases the gas cost of every deposit and withdrawal. The protocol's own comment in `setMaxUncompletedWithdrawalCount()` confirms the team is aware of the gas pressure but has only partially mitigated it by bounding one dimension while leaving `supportedAssetList` and `maxNodeDelegatorLimit` uncapped. Any unprivileged user can trigger the OOG by calling `depositETH()` or `updateRSETHPrice()` once the threshold is crossed.

## Recommendation

1. **Cache `getQueuedWithdrawals()` results per NDC**: Fetch queued withdrawals once per NDC and compute all asset amounts in a single pass, rather than calling `getAssetUnstaking()` once per NDC per asset.
2. **Hard-cap `supportedAssetList`**: Add a `maxSupportedAssets` limit analogous to `maxNodeDelegatorLimit`.
3. **Decouple accounting from live EigenLayer queries**: Store a per-NDC per-asset `unstakingAmount` updated lazily on `initiateUnstaking` / `completeUnstaking`, eliminating the live `getQueuedWithdrawals()` call from the deposit/withdrawal hot path entirely.
4. **Paginate `_getTotalEthInProtocol()`**: Allow partial updates across multiple transactions rather than computing the full TVL in one call.

## Proof of Concept

```
// Scenario: 5 supported assets, 10 NDCs, 80 queued withdrawals each, 2 strategies per withdrawal

// Step 1: Admin adds 5 LST assets to LRTConfig (routine governance)
// Step 2: Admin deploys 10 NodeDelegator contracts (routine scaling)
// Step 3: Operator queues 80 EigenLayer withdrawals across NDCs (routine unstaking)

// Step 4: Any user calls depositETH():
//   → _beforeDeposit() → getAssetCurrentLimit(ETH)
//   → getTotalAssetDeposits(ETH) → getAssetDistributionData(ETH)
//   → getETHDistributionData()
//   → for each of 10 NDCs: getAssetUnstaking(ETH)
//     → getQueuedWithdrawals() [10 calls, each returning 80 withdrawals × 2 strategies]
//   Total inner iterations: 10 × 80 × 2 = 1,600 EigenLayer storage reads

// Step 5: Any user calls updateRSETHPrice() (public, no auth):
//   → _updateRsETHPrice() → _getTotalEthInProtocol()
//   → for each of 5 assets: getTotalAssetDeposits()
//     → getAssetDistributionData() → 10 NDCs × getAssetUnstaking()
//   Total getQueuedWithdrawals() calls: 5 × 10 = 50
//   Total inner iterations: 50 × 80 × 2 = 8,000 EigenLayer storage reads

// As supportedAssets grows to 10 and maxNodeDelegatorLimit is raised to 20:
//   Total inner iterations: 10 × 20 × 80 × 2 = 32,000
//   → depositETH(), depositAsset(), updateRSETHPrice() all revert with OOG

// Foundry fork test plan:
// 1. Fork mainnet, deploy protocol with 5 assets and 10 NDCs
// 2. Queue 80 withdrawals per NDC via initiateUnstaking()
// 3. Call updateRSETHPrice() and measure gas via vm.expectRevert() or gasLeft()
// 4. Increase asset count to 10 and repeat — confirm OOG revert
```

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

**File:** contracts/LRTDepositPool.sol (L290-296)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/LRTDepositPool.sol (L482-493)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
```

**File:** contracts/LRTUnstakingVault.sol (L151-156)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;
```

**File:** contracts/LRTConfig.sol (L114-116)
```text
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
```
