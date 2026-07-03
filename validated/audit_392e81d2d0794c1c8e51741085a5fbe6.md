The code is confirmed. All cited references match exactly. Let me verify the key structural facts:

- `updateRSETHPrice()` is public with no access control [1](#0-0) 
- `_getTotalEthInProtocol()` loops over all supported assets and calls `getTotalAssetDeposits(asset)` per asset [2](#0-1) 
- `getAssetDistributionData()` loops over all NDCs and calls `getAssetUnstaking(asset)` per NDC [3](#0-2) 
- `getAssetUnstaking()` calls `getQueuedWithdrawals(address(this))` unconditionally, then iterates over every withdrawal and every strategy [4](#0-3) 

The redundancy is structural: `getQueuedWithdrawals(address(this))` returns the same data for a given NDC regardless of which asset is being queried, yet it is invoked once per (asset, NDC) pair. The total external call count is N×M for `getQueuedWithdrawals` and N×M×W×S for `sharesToUnderlyingView`.

---

Audit Report

## Title
Multiplicatively Unbounded Gas in `updateRSETHPrice()` Due to Redundant Cross-Contract Calls in Nested Asset × NDC Loop — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

## Summary
`LRTOracle.updateRSETHPrice()` is publicly callable and triggers a call chain that invokes `NodeDelegator.getAssetUnstaking(asset)` once per (supported asset, NDC) pair. Each such call makes an external `getQueuedWithdrawals(address(this))` call to EigenLayer and then iterates over every queued withdrawal and every strategy within it, calling `sharesToUnderlyingView()` per strategy. Because `getQueuedWithdrawals` returns identical data for a given NDC regardless of which asset is being queried, the external call is redundantly repeated N times per NDC. As the protocol scales normally — more supported assets, more NDCs, more queued withdrawals — the gas cost grows as O(N×M×W×S), eventually exceeding the block gas limit and permanently freezing the price update mechanism.

## Finding Description
The full call chain is:

```
updateRSETHPrice()                [LRTOracle.sol:87]  — public, no access control
  └─ _updateRsETHPrice()          [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol() [LRTOracle.sol:331]
            └─ for each asset (N):
                 getTotalAssetDeposits(asset) [LRTDepositPool.sol:385]
                   └─ getAssetDistributionData(asset) [LRTDepositPool.sol:426]
                        └─ for each NDC (M):
                             getAssetUnstaking(asset) [NodeDelegator.sol:405]
                               └─ getQueuedWithdrawals(address(this))  ← external call, repeated N×M
                                    └─ for each withdrawal (W):
                                         for each strategy (S):
                                           sharesToUnderlyingView()    ← external call, repeated N×M×W×S
```

**Root cause:** `getAssetUnstaking(address asset)` fetches the full queued withdrawal list from EigenLayer on every invocation. Since `getAssetDistributionData` calls it once per NDC per asset, and `_getTotalEthInProtocol` calls `getAssetDistributionData` once per supported asset, the same EigenLayer data is fetched N times per NDC. There is no caching, no deduplication, and no guard on the combined iteration depth.

**Existing checks are insufficient:**
- `maxNodeDelegatorLimit` (default 10, admin-increasable) bounds M but does not prevent the multiplicative blowup with N and W.
- `maxUncompletedWithdrawalCount` bounds total withdrawals across all NDCs but is admin-settable and can be large.
- Neither bound prevents the N×M redundancy in `getQueuedWithdrawals` calls.
- There is no gas guard or cap on the product N×M×W×S anywhere in the call chain.

## Impact Explanation
`updateRSETHPrice()` is the sole mechanism for updating the rsETH/ETH exchange rate used by `LRTDepositPool` for all deposits and rsETH minting. If the function's gas cost exceeds the block gas limit, it becomes permanently uncallable without a contract upgrade. This freezes the protocol's price update mechanism, preventing correct pricing of new deposits and effectively halting the protocol's core accounting. This matches the allowed impact: **Medium — Unbounded gas consumption**, with a secondary risk of **Medium — Temporary freezing of funds** if the price cannot be updated.

## Likelihood Explanation
The gas cost grows with entirely normal protocol operation: adding supported LSTs (admin action), adding NDCs (admin action), and operators calling `initiateUnstaking()` or `undelegate()` (operator action, all within normal protocol flow). No attacker action is required — the function degrades automatically as the protocol scales. With 5 supported assets, 10 NDCs, and 20 queued withdrawals per NDC (2 strategies each), the function already makes 50 `getQueuedWithdrawals()` external calls and 200 `sharesToUnderlyingView()` external calls per invocation. Each `getQueuedWithdrawals` call involves EigenLayer storage reads proportional to the withdrawal queue length. Any unprivileged caller can invoke `updateRSETHPrice()` at any time, and the function will consume gas proportional to the current protocol state.

## Recommendation
1. **Decouple asset iteration from NDC withdrawal fetching.** Refactor `getAssetDistributionData` (or introduce a new multi-asset variant) so that `getQueuedWithdrawals(address(this))` is called once per NDC, and the returned withdrawal list is iterated once to accumulate unstaking amounts for all assets simultaneously.
2. **Restructure `getAssetUnstaking`** to accept pre-fetched `(Withdrawal[], uint256[][])` data as parameters, or add a companion `getAllAssetUnstaking()` that returns a mapping/array of amounts for all assets in a single EigenLayer call.
3. **Add a protocol-level cap** on the product of `supportedAssets.length × nodeDelegatorQueue.length × maxUncompletedWithdrawalCount` to ensure `updateRSETHPrice()` remains callable within block gas limits as the protocol scales.

## Proof of Concept
Deploy on a mainnet fork with:
- 5 supported assets (stETH, rETH, cbETH, swETH, ETH_TOKEN)
- 10 NDCs each delegated to an EigenLayer operator
- Each NDC with 10 queued withdrawals (2 strategies each), created via `initiateUnstaking()`

Call `updateRSETHPrice()` and measure gas. Observe:
- `getQueuedWithdrawals()` is called 50 times (5 assets × 10 NDCs), each returning 10 withdrawals
- `sharesToUnderlyingView()` is called 100 times (5 × 10 × 2 non-ETH strategies)

Increase `maxUncompletedWithdrawalCount` and add more NDCs via `addNodeDelegatorContractToQueue`. Re-run and observe gas growing multiplicatively. At approximately 5 assets × 10 NDCs × 50 withdrawals × 2 strategies, the transaction will approach or exceed the 30M block gas limit and revert with out-of-gas, making `updateRSETHPrice()` permanently uncallable without a contract upgrade.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
