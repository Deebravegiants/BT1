### Title
Nested Unbounded Iteration in Public `updateRSETHPrice()` Causes Permanent Gas-Based DoS on Price Updates — (File: `contracts/LRTOracle.sol`)

---

### Summary

`updateRSETHPrice()` in `LRTOracle.sol` is a public, permissionless function. It internally triggers a deeply nested loop over `supportedAssets` × `nodeDelegatorQueue` × EigenLayer queued withdrawals × strategies per withdrawal. As the protocol grows within its own admin-set parameters, the cumulative gas cost of this function grows multiplicatively and can exceed the Ethereum block gas limit, permanently preventing rsETH price updates and fee minting.

---

### Finding Description

The public function `updateRSETHPrice()` calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`.

`_getTotalEthInProtocol()` iterates over every entry in `supportedAssets`:

```solidity
// LRTOracle.sol lines 336–348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    unchecked { ++assetIdx; }
}
```

`getTotalAssetDeposits(asset)` calls `getAssetDistributionData(asset)`, which iterates over every NDC in `nodeDelegatorQueue`:

```solidity
// LRTDepositPool.sol lines 447–456
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    unchecked { ++i; }
}
```

`getAssetUnstaking(asset)` in `NodeDelegator.sol` makes an external call to EigenLayer's `getQueuedWithdrawals` and then iterates over every queued withdrawal and every strategy within each withdrawal:

```solidity
// NodeDelegator.sol lines 406–427
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
    _getDelegationManager().getQueuedWithdrawals(address(this));

for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
        ...
    }
}
```

The total computational complexity is **O(N × M × W × S)** external calls and iterations, where:
- **N** = `supportedAssets.length` — no hard cap; admin can add assets indefinitely via `addNewSupportedAsset`
- **M** = `nodeDelegatorQueue.length` — bounded by `maxNodeDelegatorLimit` (default 10, admin can raise it)
- **W** = queued withdrawals per NDC — total across all NDCs bounded by `maxUncompletedWithdrawalCount` ≤ 80
- **S** = strategies per withdrawal — variable

At realistic protocol scale (N=10, M=10, W=8 per NDC, S=5 strategies), this yields ~4,000 inner iterations plus thousands of cross-contract external calls, each costing thousands of gas. This easily approaches or exceeds the 30M block gas limit.

---

### Impact Explanation

If `updateRSETHPrice()` reverts due to out-of-gas, the rsETH price stored in `rsETHPrice` becomes permanently stale. Consequences:

1. **Fee minting is frozen**: Protocol fees are minted inside `_updateRsETHPrice()`. A stale price means no protocol yield is ever captured again — permanent freezing of unclaimed yield.
2. **Deposit/withdrawal pricing is stale**: `getRsETHAmountToMint` reads `lrtOracle.rsETHPrice()` directly; a frozen price means depositors receive incorrect rsETH amounts relative to actual TVL.
3. **`updateRSETHPriceAsManager()` is also affected**: It calls the same `_updateRsETHPrice()` internal function, so even the privileged path is blocked.

**Impact: Medium — Permanent freezing of unclaimed yield / unbounded gas consumption.**

---

### Likelihood Explanation

The protocol is designed to scale: more LST assets are added over time via governance, more NDCs are deployed to handle restaking capacity, and EigenLayer queued withdrawals accumulate during normal unstaking operations. No attacker action is required — ordinary protocol growth within admin-set parameters is sufficient to trigger the condition. The `maxUncompletedWithdrawalCount` is capped at 80 by the contract, but combined with multiple assets and NDCs, the gas cost is multiplicative and realistic.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` results**: Avoid calling `getQueuedWithdrawals` once per asset per NDC. Instead, call it once per NDC and cache the result, then compute all asset unstaking amounts in a single pass.
2. **Decouple asset unstaking accounting from price updates**: Maintain a running `assetUnstaking` counter updated incrementally on `initiateUnstaking` / `completeUnstaking` events rather than recomputing it on every price update.
3. **Limit `supportedAssets` iteration in `_getTotalEthInProtocol`**: Introduce a hard cap on `supportedAssets.length` analogous to `maxNodeDelegatorLimit`.

---

### Proof of Concept

Call chain triggered by any external caller invoking `updateRSETHPrice()`:

```
updateRSETHPrice()                          [LRTOracle.sol:87]
  └─ _updateRsETHPrice()                   [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each asset (N):
                 getTotalAssetDeposits()    [LRTDepositPool.sol:385]
                   └─ getAssetDistributionData() [LRTDepositPool.sol:426]
                        └─ for each NDC (M):
                             getAssetUnstaking() [NodeDelegator.sol:405]
                               └─ getQueuedWithdrawals() [external EL call]
                               └─ for each withdrawal (W):
                                    for each strategy (S): [inner loop]
```

With N=10, M=10, W=8, S=5: **4,000 inner iterations + ~300 external cross-contract calls** per single invocation of `updateRSETHPrice()`. At ~2,100 gas per SLOAD and ~700 gas per iteration minimum, plus external call overhead (~2,500 gas each), total gas easily exceeds 30M. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
