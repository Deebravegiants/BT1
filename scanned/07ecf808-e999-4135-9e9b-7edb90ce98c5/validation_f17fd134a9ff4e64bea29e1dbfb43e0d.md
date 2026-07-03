### Title
Unbounded Gas Consumption in Publicly Callable `updateRSETHPrice()` via Nested External Loops — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function with no rate limiting or cooldown. Its gas cost scales as `O(supportedAssets × NDCs × queuedWithdrawals × strategiesPerWithdrawal)` through a chain of nested external calls. As the protocol scales — or when EigenLayer operators force undelegations that add withdrawals outside the protocol's own tracking — this function can grow to exceed the block gas limit, permanently bricking price updates and breaking the deposit/withdrawal system.

---

### Finding Description

The call chain triggered by any external caller invoking `updateRSETHPrice()` is:

1. `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()`
2. `_getTotalEthInProtocol()` loops over every entry in `supportedAssets` and calls `getTotalAssetDeposits(asset)` per asset.
3. `getTotalAssetDeposits()` calls `getAssetDistributionData()`, which loops over every entry in `nodeDelegatorQueue` and calls `INodeDelegator(ndcs[i]).getAssetUnstaking(asset)` per NDC.
4. `getAssetUnstaking()` calls EigenLayer's `DelegationManager.getQueuedWithdrawals(address(this))`, which returns **all** queued withdrawals for that NDC, then iterates over every withdrawal and every strategy within each withdrawal. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The protocol caps its own queuing via `maxUncompletedWithdrawalCount` (max 80), but EigenLayer operators can force undelegations that queue additional withdrawals entirely outside the protocol's tracking. The code itself acknowledges this: the comment in `setMaxUncompletedWithdrawalCount` states *"Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)"*. [5](#0-4) 

There is no cooldown, rate limit, or access control on `updateRSETHPrice()`. Any address can call it at any time when the contract is not paused.

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of funds.**

At maximum configured bounds (10 NDCs × 80 withdrawals × ~5 assets × multiple strategies per withdrawal), each call to `updateRSETHPrice()` executes hundreds of external calls to EigenLayer contracts. If forced undelegations push the queued withdrawal count beyond the protocol's soft cap, or if the number of supported assets and NDCs grows, the function's gas cost can exceed the Ethereum block gas limit (~30M gas). Once this threshold is crossed:

- `updateRSETHPrice()` becomes permanently uncallable.
- The stored `rsETHPrice` becomes stale.
- `initiateWithdrawal()` and `getExpectedAssetAmount()` continue to use the stale price, causing incorrect rsETH-to-asset conversions.
- The protocol's fee minting and downside-protection pause mechanism (which both depend on `_updateRsETHPrice()`) stop functioning.

---

### Likelihood Explanation

**Low-to-Medium.** Under normal operating conditions with a small number of NDCs and assets, the gas cost is manageable. However:

- The function is callable by any address with zero privilege.
- EigenLayer operator-forced undelegations are an acknowledged scenario in the codebase and are outside the protocol's control.
- As the protocol grows (more NDCs, more assets, more concurrent withdrawals), the gas cost grows multiplicatively.
- No rate limiting exists to prevent repeated calls that could interact with the price-threshold pause logic.

---

### Recommendation

1. **Add a cooldown / rate limit** on `updateRSETHPrice()` (e.g., one call per block or per N seconds) to prevent repeated invocations by unprivileged callers.
2. **Cache intermediate results** (e.g., per-NDC asset balances) rather than recomputing them on every call.
3. **Decouple `getAssetUnstaking()`** from the price-update hot path; use a separately maintained, operator-updated accounting variable for queued withdrawal amounts rather than iterating over EigenLayer's live withdrawal queue on every price update.
4. **Cap the iteration depth** explicitly in `getAssetUnstaking()` to prevent a single forced-undelegation event from making the function uncallable.

---

### Proof of Concept

```solidity
// Any external address can call this with no restriction:
ILRTOracle(oracleAddress).updateRSETHPrice();

// Internally this resolves to (simplified):
// for each asset in supportedAssets (e.g., 5 assets):
//   for each ndc in nodeDelegatorQueue (e.g., 10 NDCs):
//     DelegationManager.getQueuedWithdrawals(ndc)  // external call
//     for each withdrawal in queuedWithdrawals (e.g., 80+):
//       for each strategy in withdrawal.strategies:
//         strategy.sharesToUnderlyingView(shares)  // external call
//
// Worst-case: 5 × 10 × 80 × 3 = 12,000 external calls per updateRSETHPrice() invocation.
// At ~2,500 gas per external STATICCALL, this is ~30M gas — at or beyond the block gas limit.
// After a forced undelegation event, this permanently bricks price updates.
```

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

**File:** contracts/LRTUnstakingVault.sol (L150-158)
```text
    function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
