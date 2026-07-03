### Title
Unbounded Iteration Over `supportedAssetList` in `LRTOracle._getTotalEthInProtocol()` Causes Permanent DoS of Price Updates - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every entry in `lrtConfig.getSupportedAssetList()` with no upper bound enforced on that list. The public `updateRSETHPrice()` function calls this path. As the protocol legitimately adds more supported LST assets, the gas cost of `updateRSETHPrice()` grows without limit, eventually making it uncallable and permanently freezing the rsETH price.

---

### Finding Description

`LRTConfig._addNewSupportedAsset()` pushes to `supportedAssetList` with no cap: [1](#0-0) 

There is no `maxSupportedAssets` variable analogous to the `maxNodeDelegatorLimit` that bounds `nodeDelegatorQueue`: [2](#0-1) [3](#0-2) 

`LRTOracle._getTotalEthInProtocol()` fetches the full unbounded list and loops over every element: [4](#0-3) 

For each asset, it calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData()`, which itself loops over every NDC in `nodeDelegatorQueue`: [5](#0-4) 

And for each NDC it calls `getAssetUnstaking(asset)`, which iterates over all queued EigenLayer withdrawals and their strategies: [6](#0-5) 

The total gas is **O(supportedAssets × NDCs × queuedWithdrawals)**. While NDCs are bounded by `maxNodeDelegatorLimit` and queued withdrawals are bounded by `maxUncompletedWithdrawalCount`, `supportedAssets` has **no upper bound at all**.

The entry point `updateRSETHPrice()` is public with no role restriction: [7](#0-6) 

---

### Impact Explanation

When `supportedAssetList` grows large enough that `_getTotalEthInProtocol()` exceeds the block gas limit, `updateRSETHPrice()` becomes permanently uncallable. Consequences:

- The rsETH/ETH exchange rate is frozen at a stale value, causing depositors to receive incorrect rsETH amounts.
- The protocol fee minting mechanism (`_checkAndUpdateDailyFeeMintLimit`) inside `_updateRsETHPrice()` is permanently blocked, constituting theft of unclaimed yield.
- The downside price-protection pause (lines 270–281 of `LRTOracle.sol`) can never trigger, removing a critical safety mechanism.

**Impact: High — Theft of unclaimed yield / permanent freezing of yield; Medium — Unbounded gas consumption.** [8](#0-7) 

---

### Likelihood Explanation

Adding a new supported LST requires `TIME_LOCK_ROLE`, which is a normal, expected governance action — not an attack or compromise. The Kelp DAO protocol is explicitly designed to onboard additional LSTs over time. Each new asset linearly increases the gas cost of every `updateRSETHPrice()` call. No attacker action is required; the protocol's own growth triggers the condition.

---

### Recommendation

Add a `maxSupportedAssets` state variable to `LRTConfig` (analogous to `maxNodeDelegatorLimit` in `LRTDepositPool`) and enforce it inside `_addNewSupportedAsset()`:

```solidity
uint256 public maxSupportedAssets; // e.g., initialized to 10

function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    if (supportedAssetList.length >= maxSupportedAssets) {
        revert MaxSupportedAssetsReached();
    }
    // ... existing logic
}
``` [1](#0-0) 

---

### Proof of Concept

1. Admin (via `TIME_LOCK_ROLE`) calls `LRTConfig.addNewSupportedAsset()` repeatedly, adding N LST assets to `supportedAssetList`.
2. Any unprivileged caller invokes `LRTOracle.updateRSETHPrice()`.
3. Execution enters `_getTotalEthInProtocol()`, which loops N times. For each asset it calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → loops over M NDCs → for each NDC calls `getAssetUnstaking()` → loops over K queued withdrawals.
4. Total iterations: N × M × K. With M=10 (default `maxNodeDelegatorLimit`) and K=`maxUncompletedWithdrawalCount`, even a modest N (e.g., 20–30 assets) combined with full NDC and withdrawal queues can push gas consumption past the block limit.
5. `updateRSETHPrice()` reverts with out-of-gas on every call. The rsETH price is permanently frozen. Protocol fee minting is permanently blocked. [4](#0-3) [5](#0-4) [9](#0-8)

### Citations

**File:** contracts/LRTConfig.sol (L106-118)
```text
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

**File:** contracts/LRTDepositPool.sol (L29-30)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;
```

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-311)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
        }

        // downside protection — pause if price drops too far
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

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
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
