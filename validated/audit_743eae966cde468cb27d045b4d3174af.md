### Title
Unbounded Nested-Loop Gas Consumption in `updateRSETHPrice()` Triggered by Any Caller - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that internally executes a triple-nested loop: over all supported assets, over all NodeDelegators, and over all EigenLayer queued withdrawals per NodeDelegator. As the protocol scales, this chain can consume gas proportional to `supportedAssets × NDCs × queuedWithdrawals × strategiesPerWithdrawal`, eventually causing the function to revert out-of-gas and preventing price updates and deposits.

### Finding Description
`updateRSETHPrice()` is declared `public whenNotPaused` with no role restriction, meaning any external caller can invoke it. [1](#0-0) 

It calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. That function iterates over every entry in `supportedAssetList` and, for each asset, calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. [2](#0-1) 

`getTotalAssetDeposits` delegates to `getAssetDistributionData`, which loops over every entry in `nodeDelegatorQueue` and calls `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)` for each NDC. [3](#0-2) 

`getAssetUnstaking` fetches the full list of queued withdrawals from EigenLayer's `DelegationManager` and iterates over every withdrawal and every strategy within each withdrawal. [4](#0-3) 

The same `getAssetDistributionData` path is also triggered during every user deposit via `_checkIfDepositAmountExceedesCurrentLimit → getTotalAssetDeposits`. [5](#0-4) 

There is no explicit cap on `supportedAssetList` length. [6](#0-5) 

### Impact Explanation
**Medium — Unbounded gas consumption.** As the protocol adds more supported assets, more NodeDelegators (up to `maxNodeDelegatorLimit`, which is admin-settable), and more concurrent EigenLayer queued withdrawals (up to `maxUncompletedWithdrawalCount`), the gas cost of `updateRSETHPrice()` grows as `O(assets × NDCs × withdrawals × strategies)`. If this product exceeds the block gas limit, `updateRSETHPrice()` permanently reverts, freezing the rsETH price. Because `depositETH` and `depositAsset` also traverse the same NDC × queued-withdrawal loop per asset, they too become uncallable, temporarily freezing user deposits.

### Likelihood Explanation
The protocol is designed to support multiple LSTs and multiple NodeDelegators. EigenLayer queued withdrawals accumulate during normal operations (undelegation, strategy rebalancing). No single parameter is unreasonably large, but their product grows multiplicatively. A realistic mainnet configuration with 5 assets, 10 NDCs, and 20 queued withdrawals per NDC already produces 1,000 `getAssetUnstaking` iterations, each making an external call to EigenLayer. This is reachable without any privileged action by the attacker — the attacker simply calls `updateRSETHPrice()` after the protocol has grown to a sufficient scale, or the function naturally fails during routine operation.

### Recommendation
- Cache the result of `getAssetUnstaking` or restructure it to avoid re-querying EigenLayer's full withdrawal list on every asset × NDC combination.
- Introduce a hard cap on `supportedAssetList.length` analogous to `maxNodeDelegatorLimit`.
- Consider maintaining a running `assetUnstaking` accumulator updated incrementally on `initiateUnstaking` / `completeUnstaking` rather than recomputing it on every read.
- Add a gas-budget guard or pagination to `_getTotalEthInProtocol` so that a single call cannot exhaust the block gas limit.

### Proof of Concept
1. Protocol has 5 supported assets, 10 NDCs, and each NDC has 20 queued EigenLayer withdrawals with 3 strategies each.
2. Any EOA calls `LRTOracle.updateRSETHPrice()`.
3. Execution path: `updateRSETHPrice` → `_updateRsETHPrice` → `_getTotalEthInProtocol` → 5 × `getTotalAssetDeposits` → 5 × 10 × `getAssetUnstaking` → 50 EigenLayer `getQueuedWithdrawals` calls, each returning 20 withdrawals × 3 strategies = 3,000 inner iterations plus 50 external calls.
4. At ~5,000 gas per storage read and external call overhead, this exceeds several million gas, approaching or surpassing the Ethereum block gas limit under realistic growth, causing the transaction to revert out-of-gas.
5. With `updateRSETHPrice` reverting, the rsETH price is frozen. Simultaneously, `depositETH` calls `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits` → `getAssetDistributionData` → `getAssetUnstaking` for the deposited asset across all 10 NDCs, also reverting and blocking all new deposits.

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

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```
