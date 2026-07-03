### Title
Unbounded Gas Consumption in `updateRSETHPrice()` Due to Nested Loop Over Unbounded `supportedAssetList` - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a publicly callable function that internally executes a nested loop whose outer dimension — `supportedAssetList` — has no explicit cap and grows monotonically as the protocol adds new LSTs. As the list grows through normal protocol operation, the function's gas cost grows proportionally, eventually risking an out-of-gas revert that permanently prevents price updates.

### Finding Description
`updateRSETHPrice()` is public and `whenNotPaused`, callable by any address. It delegates to `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. [1](#0-0) 

`_getTotalEthInProtocol()` iterates over every entry in `supportedAssets` returned by `lrtConfig.getSupportedAssetList()`: [2](#0-1) 

For each asset it calls `ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset)`, which calls `getAssetDistributionData(asset)`: [3](#0-2) 

Inside that inner loop, for every NDC it calls `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)`: [4](#0-3) 

`getAssetUnstaking` itself calls EigenLayer's `getQueuedWithdrawals` and iterates over all returned withdrawals. The total gas cost is therefore **O(supportedAssets × NDCs × queuedWithdrawals)** — three nested loops, each making external calls.

The `supportedAssetList` has no explicit cap. New assets are added via `addNewSupportedAsset` (TIME_LOCK_ROLE), which is normal protocol operation for an LRT that is designed to onboard additional LSTs over time: [5](#0-4) 

`nodeDelegatorQueue` is bounded by `maxNodeDelegatorLimit` (initially 10, admin-adjustable), and queued withdrawals are bounded by `maxUncompletedWithdrawalCount` (max 80). However, `supportedAssetList` has no analogous cap. With 50 supported assets, 10 NDCs, and 80 queued withdrawals, the function would execute up to 40,000 iterations of external calls — well beyond the Ethereum block gas limit.

### Impact Explanation
`updateRSETHPrice()` is the sole mechanism for updating the rsETH/ETH exchange rate stored in `rsETHPrice`. This price is consumed by:
- `LRTDepositPool.getRsETHAmountToMint()` — used on every deposit
- `LRTWithdrawalManager.getExpectedAssetAmount()` — used on every withdrawal initiation and unlock

If `updateRSETHPrice()` becomes uncallable due to gas exhaustion, the rsETH price becomes permanently stale. The price-deviation circuit breaker in `_updateRsETHPrice()` can also auto-pause the protocol if the price drifts too far from the stale value, causing a temporary freeze of deposits and withdrawals. **Impact: Medium — Unbounded gas consumption / Temporary freezing of funds.**

### Likelihood Explanation
The LRT-rsETH protocol is explicitly designed to onboard multiple LSTs. Each new supported asset added through normal governance increases the gas cost of `updateRSETHPrice()`. No attacker action is required; the degradation occurs through routine protocol expansion. Likelihood is **Medium** — the condition is reached through expected protocol growth, not adversarial action.

### Recommendation
1. Introduce an explicit cap on `supportedAssetList` (analogous to `maxNodeDelegatorLimit` for NDCs).
2. Refactor `_getTotalEthInProtocol()` to avoid calling `getAssetUnstaking()` (which itself calls EigenLayer's `getQueuedWithdrawals`) inside the loop. Cache or pre-aggregate unstaking amounts off-chain and push them on-chain, or split the price update into per-asset batches.
3. Consider separating the TVL aggregation from the price-update path so that gas-heavy accounting does not block the critical price-update function.

### Proof of Concept
Call chain for any external caller:

```
LRTOracle.updateRSETHPrice()                          // public, whenNotPaused
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in supportedAssetList:   // NO CAP — grows with protocol
                 └─ LRTDepositPool.getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC in nodeDelegatorQueue:  // bounded by maxNodeDelegatorLimit
                                └─ NodeDelegator.getAssetUnstaking(asset)
                                     └─ DelegationManager.getQueuedWithdrawals(ndc)  // external call
                                          └─ for each queued withdrawal:  // bounded by maxUncompletedWithdrawalCount
                                               └─ strategy.sharesToUnderlyingView(...)  // external call
```

With `N` supported assets, `D` NDCs, and `W` queued withdrawals per NDC, gas scales as `O(N × D × W)`. At `N=50`, `D=10`, `W=80`, this is 40,000 iterations of external calls, exceeding the Ethereum block gas limit and permanently bricking `updateRSETHPrice()`.

### Citations

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

**File:** contracts/LRTConfig.sol (L99-118)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }

    /// @dev private function to add a new supported asset
    /// @param asset Asset address
    /// @param depositLimit Deposit limit for the asset
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```
