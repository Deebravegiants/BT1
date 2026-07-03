### Title
Nested Loops in `getAssetUnstaking` Called Per-Asset Per-NDC in `updateRSETHPrice` Cause Unbounded Gas Consumption - (File: contracts/NodeDelegator.sol)

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over all supported assets, and for each asset calls `LRTDepositPool.getAssetDistributionData()`, which in turn iterates over all NodeDelegators (NDCs) and calls `NodeDelegator.getAssetUnstaking()` on each. `getAssetUnstaking` itself contains **two nested loops** — one over all queued EigenLayer withdrawals and one over all strategies per withdrawal. The resulting complexity is O(N\_assets × M\_NDCs × P\_withdrawals × Q\_strategies), all composed of external calls. Since `updateRSETHPrice()` is public and must be called regularly to keep the rsETH price current, this unbounded gas pattern can render price updates impossible.

---

### Finding Description

The call chain is:

1. `LRTOracle.updateRSETHPrice()` (public) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()`
2. `_getTotalEthInProtocol()` loops over every supported asset and calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)`
3. `getAssetDistributionData()` loops over every NDC in `nodeDelegatorQueue` and calls `INodeDelegator(ndc).getAssetUnstaking(asset)` for each
4. `getAssetUnstaking()` calls `delegationManager.getQueuedWithdrawals(address(this))` and then runs **two nested loops**: outer over `queuedWithdrawals.length` and inner over `withdrawal.strategies.length`, making external calls to `strategy.sharesToUnderlyingView()` inside

The same pattern repeats for ETH via `getETHDistributionData()`, which also loops over all NDCs and calls `getAssetUnstaking(ETH_TOKEN)` per NDC.

**Root cause code:**

`LRTOracle._getTotalEthInProtocol()` — outer loop over assets: [1](#0-0) 

`LRTDepositPool.getAssetDistributionData()` — loop over NDCs calling `getAssetUnstaking` per NDC: [2](#0-1) 

`NodeDelegator.getAssetUnstaking()` — nested loops over queued withdrawals × strategies: [3](#0-2) 

The protocol's own comment in `LRTUnstakingVault` acknowledges the gas sensitivity of `updateRSETHPrice()`: [4](#0-3) 

The cap of 80 on `maxUncompletedWithdrawalCount` is a partial mitigation, but it does not bound the per-call gas because `getAssetUnstaking` fetches withdrawals directly from EigenLayer's `DelegationManager.getQueuedWithdrawals()` without any protocol-level cap, and the total iterations remain O(N\_assets × M\_NDCs × P\_withdrawals × Q\_strategies).

---

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit or becomes prohibitively expensive:

- The rsETH price stored in `LRTOracle.rsETHPrice` becomes permanently stale.
- Protocol fee minting is blocked (no revenue accrual).
- Deposits and withdrawals continue using the stale price, causing incorrect rsETH minting amounts and incorrect withdrawal asset amounts.
- The price-deviation circuit breaker (pause-on-drop) cannot trigger, removing a key safety mechanism.

This matches the **Medium — Unbounded gas consumption** impact class.

---

### Likelihood Explanation

The protocol already supports multiple NDCs and multiple LST assets (stETH, ETHx, sfrxETH, ETH). As the protocol scales and EigenLayer queued withdrawals accumulate during normal unstaking operations, the gas cost grows multiplicatively. The `maxUncompletedWithdrawalCount` cap (set to ≤80 total) does not prevent the issue because:

1. `getAssetUnstaking` bypasses the protocol cap by reading directly from EigenLayer.
2. Forced operator undelegations (acknowledged in the comment as "ndc count × asset count = 15") can add withdrawals outside the cap.
3. Each queued withdrawal can contain multiple strategies, multiplying the inner loop count.

With 3 assets, 5 NDCs, 16 withdrawals per NDC (80 total / 5 NDCs), and 3 strategies per withdrawal, the call to `updateRSETHPrice()` already involves 3 × 5 × 16 × 3 = 720 external strategy calls, each with associated memory allocation and cross-contract overhead.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` once per NDC** and reuse across all asset queries, eliminating the per-asset re-fetch.
2. **Maintain a running TVL accumulator** updated on each deposit/withdrawal to the NDC ("push" pattern), so `updateRSETHPrice()` only needs to read a single cached value per asset.
3. **Bound the inner loop** by enforcing a per-NDC withdrawal count cap at the `NodeDelegator` level, not just a global total in `LRTUnstakingVault`.
4. Alternatively, use an off-chain oracle to supply the TVL value, removing on-chain iteration entirely.

---

### Proof of Concept

**Call chain for a single `updateRSETHPrice()` call with N=3 assets, M=5 NDCs, P=16 queued withdrawals per NDC, Q=3 strategies per withdrawal:**

```
updateRSETHPrice()
└── _getTotalEthInProtocol()
    └── [loop: 3 assets]
        └── getTotalAssetDeposits(asset)
            └── getAssetDistributionData(asset)
                └── [loop: 5 NDCs]
                    └── getAssetUnstaking(asset)   // external call per NDC per asset
                        └── delegationManager.getQueuedWithdrawals(ndc)
                            └── [loop: 16 withdrawals]
                                └── [loop: 3 strategies]
                                    └── strategy.sharesToUnderlyingView(shares)  // external call
```

Total external `sharesToUnderlyingView` calls: 3 × 5 × 16 × 3 = **720**

Plus 3 × 5 = 15 calls to `delegationManager.getQueuedWithdrawals()`, each returning and allocating memory for the full withdrawal array. Memory expansion costs grow quadratically with array size. At these iteration counts, `updateRSETHPrice()` will consume several million gas, approaching or exceeding the block gas limit on L1.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L447-456)
```text
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

**File:** contracts/LRTUnstakingVault.sol (L151-155)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
```
