Audit Report

## Title
Unbounded Nested-Loop Gas Consumption in `updateRSETHPrice()` Triggered by Any Caller - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that executes a multiplicative chain of loops and external calls: over all supported assets, over all NodeDelegators, and over all EigenLayer queued withdrawals per NodeDelegator. As the protocol scales, this chain can consume gas proportional to `supportedAssets × NDCs × queuedWithdrawals × strategiesPerWithdrawal`, eventually causing the function to revert out-of-gas and permanently freezing the rsETH price. The same traversal path is triggered on every user deposit, blocking deposits as well.

## Finding Description
`updateRSETHPrice()` is declared `public whenNotPaused` with no role restriction, callable by any EOA. [1](#0-0) 

It calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()`, which iterates over every entry in `supportedAssetList` and calls `ILRTDepositPool.getTotalAssetDeposits(asset)` for each. [2](#0-1) 

`getTotalAssetDeposits` delegates to `getAssetDistributionData`, which loops over every entry in `nodeDelegatorQueue` and calls `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)` for each NDC — one external call per NDC per asset. [3](#0-2) 

`getAssetUnstaking` fetches the full list of queued withdrawals from EigenLayer's `DelegationManager` via `getQueuedWithdrawals(address(this))` and iterates over every withdrawal and every strategy within each withdrawal. [4](#0-3) 

The same `getAssetDistributionData` path is triggered on every user deposit via `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits`. [5](#0-4) 

**Existing guards are insufficient:**
- `maxNodeDelegatorLimit` is initialized to 10 but is admin-settable with no hard upper bound in the code. [6](#0-5) 

- `maxUncompletedWithdrawalCount` is a global cap across all NDCs, not per-NDC. It bounds total withdrawals but does not prevent `assets × NDCs` external calls to `getQueuedWithdrawals` regardless of withdrawal count.
- `supportedAssetList` has no explicit length cap; assets are added via `TIME_LOCK_ROLE` with no maximum enforced. [7](#0-6) 

## Impact Explanation
**Medium — Unbounded gas consumption.** The gas cost of `updateRSETHPrice()` grows as `O(assets × NDCs × withdrawals × strategies)`. If this product exceeds the block gas limit (~30M gas on Ethereum mainnet), `updateRSETHPrice()` permanently reverts, freezing the rsETH price. Because `depositETH` and `depositAsset` traverse the same NDC × queued-withdrawal loop per deposited asset, they also revert, temporarily freezing all user deposits. This matches the allowed impact "Medium. Unbounded gas consumption."

## Likelihood Explanation
No privileged action by an attacker is required. The attacker simply calls `updateRSETHPrice()` after the protocol has grown to sufficient scale, or the function fails naturally during routine operation. A realistic mainnet configuration with 5 supported assets, 10 NDCs, and 20 queued EigenLayer withdrawals per NDC produces 50 external calls to `getQueuedWithdrawals` plus 1,000 inner strategy iterations. Each external call carries significant gas overhead (~2,100 gas for the CALL opcode plus EigenLayer storage reads). The `undelegate()` path can create multiple withdrawals per NDC in a single transaction, accelerating accumulation. No single parameter is unreasonably large, but their product grows multiplicatively under normal protocol operation.

## Recommendation
- Maintain a running `assetUnstaking` accumulator updated incrementally on `initiateUnstaking` / `completeUnstaking` / `undelegate` rather than recomputing it on every read via `getQueuedWithdrawals`.
- Introduce a hard cap on `supportedAssetList.length` analogous to `maxNodeDelegatorLimit`.
- Add a per-NDC cap on uncompleted withdrawals (rather than only a global cap) to bound the per-call cost of `getAssetUnstaking`.
- Consider a gas-budget guard or pagination in `_getTotalEthInProtocol` so a single call cannot exhaust the block gas limit.

## Proof of Concept
1. Deploy protocol with 5 supported assets, 10 NDCs (`maxNodeDelegatorLimit = 10`), and `maxUncompletedWithdrawalCount = 100`.
2. Operator calls `initiateUnstaking` across NDCs until each NDC has ~10 queued withdrawals with 3 strategies each (total 100 withdrawals, within the global cap).
3. Any EOA calls `LRTOracle.updateRSETHPrice()`.
4. Execution path: `updateRSETHPrice` → `_updateRsETHPrice` → `_getTotalEthInProtocol` → 5× `getTotalAssetDeposits` → 5×10 = 50 external calls to `getQueuedWithdrawals`, each returning ~10 withdrawals × 3 strategies = 1,500 inner iterations plus 50 external calls.
5. Foundry fork test: instrument gas usage at each loop level; assert that total gas consumed approaches or exceeds 15–20M gas, demonstrating the multiplicative growth. Increase NDC count or withdrawal count to demonstrate revert at block gas limit.
6. Separately, call `depositAsset` for any asset and observe it traverses the same path for that single asset across all 10 NDCs, also reverting if the per-asset NDC × withdrawal product is large enough.

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

**File:** contracts/LRTDepositPool.sol (L290-296)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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
