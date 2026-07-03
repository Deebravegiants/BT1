### Title
Nested Loops Over NDCs and EigenLayer Queued Withdrawals in `getAssetUnstaking()` Cause Unbounded Gas Consumption in `updateRSETHPrice()` and User Deposits — (File: `contracts/NodeDelegator.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`NodeDelegator.getAssetUnstaking()` fetches and iterates over all queued EigenLayer withdrawals. This function is called inside a nested loop: once per NodeDelegator (NDC) per supported asset, both in `LRTDepositPool.getAssetDistributionData()` and transitively in `LRTOracle._getTotalEthInProtocol()`. The public `LRTOracle.updateRSETHPrice()` and user-facing `depositAsset()`/`depositETH()` both trigger this nested loop, creating a gas cost that scales as O(assets × NDCs × queued\_withdrawals × strategies\_per\_withdrawal).

---

### Finding Description

**Root cause — `NodeDelegator.getAssetUnstaking()`:** [1](#0-0) 

The function calls `_getDelegationManager().getQueuedWithdrawals(address(this))` — an external call that returns every pending EigenLayer withdrawal for that NDC — and then iterates over all returned withdrawals and all strategies within each withdrawal.

**First nesting layer — `LRTDepositPool.getAssetDistributionData()`:** [2](#0-1) 

For every supported asset, this function loops over the entire `nodeDelegatorQueue` and calls `getAssetUnstaking()` on each NDC. With `maxNodeDelegatorLimit = 10` NDCs and up to 80 queued withdrawals per NDC (the admin-acknowledged cap), this already produces up to 10 external calls to EigenLayer's `DelegationManager` plus hundreds of in-memory iterations per asset.

**Second nesting layer — `LRTOracle._getTotalEthInProtocol()`:** [3](#0-2) 

This function loops over every entry in `supportedAssetList` and calls `getTotalAssetDeposits()` → `getAssetDistributionData()` for each. With N supported assets, the total number of `getQueuedWithdrawals()` external calls becomes **N\_assets × N\_NDCs** (e.g., 5 × 10 = 50 external calls), and the iteration count becomes **N\_assets × N\_NDCs × N\_withdrawals × N\_strategies** (e.g., 5 × 10 × 8 × 2 = 800 iterations).

The same queued-withdrawal data for each NDC is fetched redundantly once per supported asset, with no caching.

**Public entry point — `LRTOracle.updateRSETHPrice()`:** [4](#0-3) 

This function is `public whenNotPaused` — callable by any address with no access restriction.

**User deposit entry point:** [5](#0-4) 

Every call to `depositAsset()` or `depositETH()` invokes `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()`, triggering the NDC loop and `getAssetUnstaking()` for the deposited asset.

The developers themselves acknowledge the gas concern in `LRTUnstakingVault.sol`: [6](#0-5) 

> "120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of funds.**

As the protocol scales (more supported assets, more NDCs, more concurrent EigenLayer withdrawals), the gas cost of `updateRSETHPrice()` and `depositAsset()`/`depositETH()` grows multiplicatively. If the gas cost approaches or exceeds the block gas limit:

1. `updateRSETHPrice()` becomes uncallable, freezing the rsETH price at a stale value and breaking the fee-minting mechanism.
2. `depositAsset()` / `depositETH()` revert, temporarily freezing user deposits into the protocol.

---

### Likelihood Explanation

**Medium.** The protocol is deployed on Ethereum mainnet. The admin-set caps (`maxNodeDelegatorLimit = 10`, `maxUncompletedWithdrawalCount ≤ 80`) are legitimate operational values, not adversarial. As the protocol grows — more assets added, more NDCs deployed, more concurrent EigenLayer unstaking operations — the gas cost naturally increases toward the problematic range without any attacker action. Any user can trigger `updateRSETHPrice()` to observe or force the failure.

---

### Recommendation

1. **Cache `getQueuedWithdrawals()` per NDC** rather than calling it once per asset per NDC. A single call per NDC can serve all assets.
2. **Accumulate a running `totalUnstaking` counter** (incremented on `initiateUnstaking`, decremented on `completeUnstaking`) per asset per NDC, eliminating the need to iterate over EigenLayer's withdrawal queue at read time — analogous to the recommendation in the external report.
3. **Apply a hard cap** on `supportedAssetList` length in addition to the existing NDC and withdrawal caps.

---

### Proof of Concept

Call chain for `updateRSETHPrice()` (callable by any user):

```
LRTOracle.updateRSETHPrice()
  └─ _getTotalEthInProtocol()                          // loops over supportedAssets (N_assets)
       └─ LRTDepositPool.getTotalAssetDeposits(asset)
            └─ getAssetDistributionData(asset)         // loops over nodeDelegatorQueue (N_ndcs)
                 └─ NodeDelegator.getAssetUnstaking(asset)
                      └─ DelegationManager.getQueuedWithdrawals(ndc)  // external call, returns up to 80 withdrawals
                           └─ for each withdrawal:                    // loops over N_withdrawals
                                for each strategy:                    // loops over N_strategies
                                    ...
```

Total external calls to EigenLayer: `N_assets × N_ndcs` (e.g., 5 × 10 = **50 external calls**).
Total inner iterations: `N_assets × N_ndcs × N_withdrawals × N_strategies` (e.g., 5 × 10 × 8 × 2 = **800 iterations**).

The same path is triggered on every `depositAsset()` / `depositETH()` call (for a single asset, so `N_ndcs × N_withdrawals × N_strategies` iterations per deposit).

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

**File:** contracts/LRTUnstakingVault.sol (L151-153)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
```
