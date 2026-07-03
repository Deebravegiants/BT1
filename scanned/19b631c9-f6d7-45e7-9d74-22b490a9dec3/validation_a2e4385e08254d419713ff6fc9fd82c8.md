### Title
Unbounded Nested Gas Loop in `updateRSETHPrice` Causes Permanent DoS of Price Updates - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function that internally executes a deeply nested loop across all supported assets, all node delegators, and all queued EigenLayer withdrawals per NDC. As the protocol scales, this function will exceed the block gas limit, permanently preventing any caller from updating the rsETH price.

---

### Finding Description

The call chain is:

```
updateRSETHPrice()                          [LRTOracle.sol:87]  — public, no access control
  └─ _updateRsETHPrice()                    [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each supportedAsset      [LRTOracle.sol:336]
                 └─ getTotalAssetDeposits() [LRTDepositPool.sol:385]
                      └─ getAssetDistributionData() [LRTDepositPool.sol:426]
                           └─ for each NDC in nodeDelegatorQueue [LRTDepositPool.sol:447]
                                └─ getAssetUnstaking(asset) [NodeDelegator.sol:405]
                                     └─ for each queuedWithdrawal [NodeDelegator.sol:409]
                                          └─ for each strategy in withdrawal [NodeDelegator.sol:412]
```

**Level 1 — Asset loop** in `_getTotalEthInProtocol()`: [1](#0-0) 

**Level 2 — NDC loop** in `getAssetDistributionData()`: [2](#0-1) 

**Level 3 — Nested withdrawal × strategy loop** in `getAssetUnstaking()`: [3](#0-2) 

For the ETH asset path, `getAssetDistributionData` delegates to `getETHDistributionData()`, which also loops over all NDCs and calls both `getEffectivePodShares()` and `getAssetUnstaking(ETH_TOKEN)` per NDC: [4](#0-3) 

The total gas cost scales as:

```
O(assets × NDCs × queuedWithdrawals × strategiesPerWithdrawal)
```

Each `getAssetUnstaking` call also invokes `strategy.sharesToUnderlyingView()` on an external EigenLayer strategy contract, adding an external call overhead per strategy per withdrawal per NDC per asset.

---

### Impact Explanation

`updateRSETHPrice()` is the sole mechanism for refreshing the rsETH/ETH exchange rate stored in `rsETHPrice`. If this function becomes uncallable due to gas exhaustion:

1. **rsETH price becomes permanently stale** — the stored `rsETHPrice` is used directly in `getRsETHAmountToMint()` for all deposits, meaning users receive incorrect rsETH amounts.
2. **Protocol fee minting halts** — `_checkAndUpdateDailyFeeMintLimit` inside `_updateRsETHPrice` is never reached, so protocol revenue accrual stops.
3. **Downside price-protection cannot trigger** — the automatic pause logic that fires when price drops beyond `pricePercentageLimit` is inside `_updateRsETHPrice` and becomes unreachable, removing a critical safety mechanism.

Impact: **Medium — Temporary (escalating to permanent) freezing of the price update function, with secondary stale-price impact on all deposits.**

---

### Likelihood Explanation

The protocol already supports multiple LST assets (stETH, ethX, sfrxETH) and up to `maxNodeDelegatorLimit` NDCs (initialized to 10, governable upward). EigenLayer queued withdrawals accumulate naturally during normal unstaking operations; `maxUncompletedWithdrawalCount` is capped at 80. With 3 assets × 10 NDCs × 80 withdrawals × N strategies, the loop count is already in the thousands of external calls. This is a realistic operational state, not a theoretical extreme. [5](#0-4) [6](#0-5) 

---

### Recommendation

1. **Decouple the price update from full on-chain enumeration**: Cache per-NDC asset balances and update them incrementally (e.g., on deposit/withdrawal events) rather than re-enumerating everything on each price update.
2. **Separate `getAssetUnstaking` from the price path**: Queued withdrawal enumeration is the deepest loop; consider maintaining a running `totalUnstaking[asset]` counter updated on `initiateUnstaking` / `completeQueuedWithdrawal` instead of re-scanning EigenLayer's withdrawal queue.
3. **Bound the loop explicitly**: If full enumeration is kept, add a hard cap on the number of iterations and revert with a descriptive error if exceeded, so the failure is explicit rather than an out-of-gas revert.

---

### Proof of Concept

Attacker-controlled entry path (no privileges required):

```solidity
// Any EOA or contract can call:
ILRTOracle(lrtOracleAddress).updateRSETHPrice();
// With:
//   supportedAssets.length = 3 (stETH, ethX, sfrxETH + ETH)
//   nodeDelegatorQueue.length = 10
//   queuedWithdrawals per NDC = 8 (maxUncompletedWithdrawalCount / NDC count)
//   strategies per withdrawal = 1-3
// Total external calls: 3 * 10 * 8 * 2 = 480+ external calls in a single tx
// As NDCs and withdrawals grow, this exceeds block gas limit
```

The public entry point: [7](#0-6) 

The unbounded asset enumeration feeding into the NDC loop: [8](#0-7) 

The per-asset NDC loop calling the innermost nested withdrawal scanner: [9](#0-8)

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

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
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

**File:** contracts/NodeDelegator.sol (L409-426)
```text
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
```

**File:** contracts/LRTUnstakingVault.sol (L153-153)
```text
        if (_maxUncompletedWithdrawalCount > 80) {
```
