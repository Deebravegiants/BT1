### Title
Nested Unbounded Loops in `updateRSETHPrice()` Across `LRTOracle`, `LRTDepositPool`, and `NodeDelegator` Can Permanently Brick the Price Oracle - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol, contracts/NodeDelegator.sol)

### Summary
The public `updateRSETHPrice()` function in `LRTOracle` triggers a deeply nested call chain that iterates over supported assets × node delegators × EigenLayer queued withdrawals × strategies per withdrawal. As the protocol scales normally (more assets, more NDCs, more queued EigenLayer withdrawals), the cumulative gas cost of this chain can exceed the block gas limit, permanently rendering `updateRSETHPrice()` uncallable and freezing the rsETH price oracle.

### Finding Description

The call chain is:

```
updateRSETHPrice()                          [LRTOracle.sol:87]
  └─ _updateRsETHPrice()                   [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each supportedAsset:
                 getTotalAssetDeposits()    [LRTDepositPool.sol:385]
                   └─ getAssetDistributionData()  [LRTDepositPool.sol:426]
                        └─ for each NDC in nodeDelegatorQueue:
                             getAssetUnstaking()  [NodeDelegator.sol:405]
                               └─ getQueuedWithdrawals() [EigenLayer external call]
                                    └─ for each queued withdrawal:
                                         for each strategy in withdrawal:
                                              sharesToUnderlyingView() [external call]
```

**Layer 1 — `_getTotalEthInProtocol()` iterates over all supported assets:** [1](#0-0) 

**Layer 2 — `getAssetDistributionData()` iterates over all NDCs per asset:** [2](#0-1) 

**Layer 3 — `getAssetUnstaking()` calls EigenLayer and iterates over all queued withdrawals and their strategies per NDC:** [3](#0-2) 

Each iteration at Layer 3 performs:
- One external `STATICCALL` to EigenLayer's `DelegationManager.getQueuedWithdrawals()` (which itself reads unbounded storage)
- One external `STATICCALL` to `strategy.sharesToUnderlyingView()` per strategy per withdrawal

The total number of external calls is `O(assets × NDCs × queuedWithdrawals × strategiesPerWithdrawal)`. With `maxNodeDelegatorLimit = 10`, 5 supported assets, and even a modest `maxUncompletedWithdrawalCount`, the gas cost can easily approach or exceed the 30M block gas limit on Ethereum mainnet.

The public entry point requires no privilege: [4](#0-3) 

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit it becomes permanently uncallable. `updateRSETHPriceAsManager()` calls the same internal `_updateRsETHPrice()` and is equally affected: [5](#0-4) 

Consequences:
- The `rsETHPrice` storage variable is permanently frozen at its last value.
- Protocol fee minting via `IRSETH.mint()` inside `_updateRsETHPrice()` is permanently blocked, constituting permanent freezing of unclaimed yield (fee revenue).
- All deposit and withdrawal pricing (`getRsETHAmountToMint`, `getExpectedAssetAmount`) silently use a stale price, causing systematic mispricing for all users.

**Impact: Medium — Unbounded gas consumption / Permanent freezing of unclaimed yield.**

### Likelihood Explanation

The protocol is designed to scale: `maxNodeDelegatorLimit` can be raised by admin, new LST assets can be added to `supportedAssets`, and EigenLayer queued withdrawals accumulate during normal unstaking operations. No malicious actor is required; ordinary protocol growth through legitimate admin and operator actions is sufficient to trigger the condition. The `maxUncompletedWithdrawalCount` bound does not prevent the gas issue because `getAssetUnstaking` is called once per NDC per asset, multiplying the external call count.

**Likelihood: Medium** — Triggered by normal protocol scaling, not adversarial action.

### Recommendation

1. **Cache `getQueuedWithdrawals` results**: In `getAssetUnstaking`, the call to `getQueuedWithdrawals` is repeated for every `(NDC, asset)` pair. Refactor `_getTotalEthInProtocol` to fetch queued withdrawals once per NDC and compute all asset balances in a single pass.
2. **Decouple asset accounting from live EigenLayer queries**: Store a cached `assetUnstaking` value per NDC per asset that is updated lazily (e.g., when withdrawals are queued or completed) rather than recomputed on every oracle update.
3. **Bound the iteration explicitly**: Add a hard cap on the product `assets × NDCs` and document the maximum safe `maxUncompletedWithdrawalCount` relative to the block gas limit.
4. **Split `updateRSETHPrice` into paginated calls** if the full computation cannot be made O(1).

### Proof of Concept

Assume:
- 5 supported assets (ETH, stETH, ETHx, rETH, sfrxETH)
- 10 NDCs (`maxNodeDelegatorLimit = 10`)
- 20 queued EigenLayer withdrawals per NDC (within `maxUncompletedWithdrawalCount`)
- 2 strategies per withdrawal

Total external calls in one `updateRSETHPrice()` invocation:
- `getQueuedWithdrawals`: 5 assets × 10 NDCs = **50 external calls**
- `sharesToUnderlyingView`: 50 × 20 withdrawals × 2 strategies = **2,000 external calls**

At ~5,000 gas per cold external call minimum, plus storage reads inside EigenLayer, this easily exceeds 30M gas. Once this threshold is crossed, `updateRSETHPrice()` and `updateRSETHPriceAsManager()` both revert on every call, permanently freezing the oracle and all fee minting.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L333-348)
```text
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
