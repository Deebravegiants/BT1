### Title
Nested Loop in `updateRSETHPrice` Across Supported Assets, Node Delegators, and EigenLayer Queued Withdrawals Can Permanently Brick Price Updates - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public function that internally executes a triple-nested loop: once over all supported assets, once over all node delegators per asset, and once over all EigenLayer queued withdrawals per node delegator. As the protocol scales to its configured operational limits, this function can permanently exceed the block gas limit, making the rsETH price permanently stale and disabling fee minting and price-based pause protection.

---

### Finding Description

The public `updateRSETHPrice()` function calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()`. Inside `_getTotalEthInProtocol()`, the code iterates over every supported asset and calls `getTotalAssetDeposits(asset)` on the deposit pool: [1](#0-0) 

`getTotalAssetDeposits` calls `getAssetDistributionData`, which iterates over every entry in `nodeDelegatorQueue` and calls `getAssetUnstaking(asset)` on each: [2](#0-1) 

`getAssetUnstaking` in `NodeDelegator` fetches **all** queued withdrawals from EigenLayer's `DelegationManager` and iterates over them with a nested loop over strategies per withdrawal: [3](#0-2) 

The total gas cost scales as:

```
|supportedAssets| × |nodeDelegatorQueue| × |queuedWithdrawals_per_NDC| × |strategies_per_withdrawal|
```

- `supportedAssets` has no hard cap; assets are added via `TIME_LOCK_ROLE` with no maximum enforced: [4](#0-3) 

- `nodeDelegatorQueue` is capped by `maxNodeDelegatorLimit` (default 10), which is freely raisable by admin: [5](#0-4) 

- Queued withdrawals per NDC are capped by `maxUncompletedWithdrawalCount` in `LRTUnstakingVault`, also admin-configurable: [6](#0-5) 

Each of these parameters is set independently for legitimate operational reasons. No single parameter appears dangerous in isolation, but their product can easily exceed the block gas limit (30M gas on Ethereum mainnet) at normal operational scale (e.g., 10 assets × 10 NDCs × 50 queued withdrawals × 2 strategies = 10,000 external calls).

---

### Impact Explanation

If `updateRSETHPrice()` permanently OOGs:

1. The stored `rsETHPrice` becomes permanently stale. Both `getRsETHAmountToMint` (deposit path) and `getExpectedAssetAmount` (withdrawal path) consume this stale value, causing all users to receive incorrect rsETH or asset amounts: [7](#0-6) [8](#0-7) 

2. Protocol fee minting stops entirely, as fees are only minted inside `_updateRsETHPrice()`: [9](#0-8) 

3. The price-based automatic pause protection (which pauses the protocol on large price drops) stops functioning: [10](#0-9) 

Impact: **Medium** — unbounded gas consumption permanently disabling price updates, with secondary effects of stale exchange rates for all depositors and withdrawers, and loss of yield (fee minting).

---

### Likelihood Explanation

The protocol is designed to scale: more LSTs are added over time, more NDCs are deployed to handle restaking capacity, and each NDC accumulates queued EigenLayer withdrawals during normal operation. No single admin action is reckless; the combination of reasonable operational parameters naturally reaches the OOG threshold. This mirrors the original finding's judge comment: *"the limitation might be reached by natural means."* No attacker action is required — the function simply becomes uncallable as the protocol grows.

---

### Recommendation

1. **Decouple `getAssetUnstaking` from the price update path.** Cache the unstaking amount in storage and update it lazily (e.g., when `initiateUnstaking` / `completeUnstaking` are called) rather than recomputing it via a live EigenLayer query on every price update.

2. **Alternatively**, remove the `getAssetUnstaking` contribution from `_getTotalEthInProtocol` and account for it separately, since assets in the EigenLayer withdrawal queue are already committed and their value does not change the rsETH price until they are received.

3. **Add a hard cap** on `maxNodeDelegatorLimit` and `maxUncompletedWithdrawalCount` that is validated against the block gas limit.

---

### Proof of Concept

Call chain that leads to OOG:

```
updateRSETHPrice()                          [LRTOracle.sol:87]
  └─ _updateRsETHPrice()                    [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each asset in supportedAssets:
                 getTotalAssetDeposits(asset)  [LRTDepositPool.sol:385]
                   └─ getAssetDistributionData(asset) [LRTDepositPool.sol:426]
                        └─ for each NDC in nodeDelegatorQueue:
                             getAssetUnstaking(asset)  [NodeDelegator.sol:405]
                               └─ DelegationManager.getQueuedWithdrawals(NDC)
                                    └─ for each withdrawal:
                                         for each strategy:
                                              strategy.sharesToUnderlyingView(...)
```

With 10 supported assets, 10 NDCs, and 50 queued withdrawals each containing 2 strategies, this executes **10,000 external calls** in a single transaction. At ~2,100 gas per `STATICCALL` plus EigenLayer internal logic, this exceeds 30M gas and permanently reverts every call to `updateRSETHPrice()`.

### Citations

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
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

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTUnstakingVault.sol (L39-41)
```text
    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;

```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
