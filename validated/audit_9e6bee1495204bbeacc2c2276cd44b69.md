### Title
Unbounded Gas Consumption in Deposit and Price-Update Paths via Nested Loops Over NDCs and EigenLayer Queued Withdrawals - (File: contracts/NodeDelegator.sol, contracts/LRTOracle.sol, contracts/LRTDepositPool.sol)

### Summary
`NodeDelegator.getAssetUnstaking()` performs a nested loop over all EigenLayer queued withdrawals for a given NDC. This function is called once per NDC per supported asset inside `getAssetDistributionData()` / `getETHDistributionData()`, which are themselves called on every user deposit (via `_checkIfDepositAmountExceedesCurrentLimit`) and on every call to the publicly accessible `updateRSETHPrice()`. As the number of supported assets, NDCs, and queued EigenLayer withdrawals grows, the aggregate gas cost of these paths grows as O(assets × NDCs × queuedWithdrawals × strategiesPerWithdrawal), with no on-chain cap preventing the block gas limit from being exceeded.

### Finding Description

`LRTOracle.updateRSETHPrice()` is public with no access-control restriction (only `whenNotPaused`). It calls `_getTotalEthInProtocol()`, which iterates over every supported asset and for each calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. [1](#0-0) [2](#0-1) 

`getTotalAssetDeposits` delegates to `getAssetDistributionData` / `getETHDistributionData`, both of which loop over every entry in `nodeDelegatorQueue` and call `INodeDelegator.getAssetUnstaking(asset)` for each NDC: [3](#0-2) [4](#0-3) 

`getAssetUnstaking` fetches the full list of queued withdrawals from EigenLayer's `DelegationManager` and iterates over them with a nested loop: [5](#0-4) 

The same `getTotalAssetDeposits` call chain is triggered on every user deposit through `_checkIfDepositAmountExceedesCurrentLimit`: [6](#0-5) [7](#0-6) 

The total gas cost per call is therefore:

```
O(supportedAssets × |nodeDelegatorQueue| × queuedWithdrawals_per_NDC × strategies_per_withdrawal)
```

There is no single on-chain cap on this product. `maxNodeDelegatorLimit` bounds NDC count (default 10), and `maxUncompletedWithdrawalCount` bounds queued withdrawals per NDC, but neither is coordinated with the other or with the number of supported assets to guarantee the combined iteration stays within the block gas limit. [8](#0-7) 

### Impact Explanation

When the product of (supported assets) × (NDC count) × (queued withdrawals per NDC) × (strategies per withdrawal) grows large enough, both `depositETH`/`depositAsset` and `updateRSETHPrice` will revert with out-of-gas. This causes:

- **Temporary freezing of funds**: users cannot deposit, and existing depositors cannot trigger price updates needed for withdrawals to be processed correctly.
- **Medium severity** per the allowed impact scope: unbounded gas consumption / temporary freezing of funds.

### Likelihood Explanation

The protocol is designed to scale: `maxNodeDelegatorLimit` can be raised by admin, multiple assets are supported, and EigenLayer queued withdrawals accumulate during normal operation. With 5 supported assets, 10 NDCs, and 50 queued withdrawals each (all within normal operational bounds), the inner loop executes ≥2,500 times per `updateRSETHPrice` call, each iteration involving external calls to EigenLayer strategy contracts. This is realistic at production scale and requires no attacker action beyond calling the public `updateRSETHPrice()` or `depositETH()` functions.

### Recommendation

1. **Cache `getAssetUnstaking` results**: Compute the total unstaking amount once per NDC across all assets in a single pass rather than calling it once per (NDC, asset) pair.
2. **Decouple price update from full TVL scan**: Store a running TVL that is updated incrementally rather than recomputed from scratch on every call.
3. **Bound the combined iteration**: Enforce an explicit cap on `supportedAssets × maxNodeDelegatorLimit × maxUncompletedWithdrawalCount` at the admin configuration layer.
4. **Paginate or snapshot EigenLayer queued withdrawals**: Instead of calling `getQueuedWithdrawals` (which returns the full unbounded list) on every view, maintain an internal accounting of unstaking amounts updated at queue/complete time.

### Proof of Concept

Call trace for `depositETH(0, "")`:

```
LRTDepositPool.depositETH()
  └─ _beforeDeposit()
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
            └─ getTotalAssetDeposits(ETH_TOKEN)
                 └─ getETHDistributionData()
                      └─ for i in [0..ndcsCount):          // up to maxNodeDelegatorLimit (e.g. 10)
                           INodeDelegator(ndcs[i]).getAssetUnstaking(ETH_TOKEN)
                             └─ DelegationManager.getQueuedWithdrawals(ndc)
                                  // returns up to maxUncompletedWithdrawalCount entries
                             └─ for w in queuedWithdrawals:   // e.g. 50
                                  for s in withdrawal.strategies:  // e.g. 3
                                    strategy.sharesToUnderlyingView(shares)  // external call
```

Call trace for `updateRSETHPrice()` (public, no auth):

```
LRTOracle.updateRSETHPrice()
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for asset in supportedAssets:          // e.g. 5 assets
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for i in [0..ndcsCount):   // e.g. 10 NDCs
                             getAssetUnstaking(asset)
                               └─ [same nested loop as above]
```

Total iterations: 5 × 10 × 50 × 3 = **7,500 external calls** per `updateRSETHPrice` invocation, sufficient to exceed the Ethereum block gas limit (30M gas) at realistic protocol scale. [1](#0-0) [9](#0-8) [10](#0-9)

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

**File:** contracts/LRTDepositPool.sol (L303-306)
```text
        uint256 length = nodeDelegatorContracts.length;
        if (nodeDelegatorQueue.length + length > maxNodeDelegatorLimit) {
            revert MaximumNodeDelegatorLimitReached();
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

**File:** contracts/LRTDepositPool.sol (L661-665)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
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
