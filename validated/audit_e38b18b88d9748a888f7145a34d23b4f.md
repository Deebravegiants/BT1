### Title
Unbounded Nested Loops in `getAssetDistributionData` and `_getTotalEthInProtocol` Cause OOG, Temporarily Freezing Deposits and Price Updates - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

---

### Summary

`LRTDepositPool.getAssetDistributionData()` and `LRTOracle._getTotalEthInProtocol()` contain nested unbounded loops that iterate over `nodeDelegatorQueue`, and for each NDC call `NodeDelegator.getAssetUnstaking()`, which itself contains a nested loop over all queued EigenLayer withdrawals and their strategies. As the protocol scales, these loops can exceed the block gas limit, causing user-facing deposit transactions and the public `updateRSETHPrice()` call to revert with out-of-gas, temporarily freezing deposits and staling the rsETH price oracle.

---

### Finding Description

**Loop chain 1 — user deposit path:**

`depositETH()` / `depositAsset()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()`.

Inside `getAssetDistributionData()`, a loop iterates over every entry in `nodeDelegatorQueue`:

```solidity
// LRTDepositPool.sol L447-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    unchecked { ++i; }
}
```

Each call to `INodeDelegator.getAssetUnstaking(asset)` executes a **nested loop** in `NodeDelegator.getAssetUnstaking()`:

```solidity
// NodeDelegator.sol L409-426
for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    ...
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
        ...
    }
}
```

The `queuedWithdrawals` array is fetched live from EigenLayer's `DelegationManager.getQueuedWithdrawals()` and is unbounded — it grows with every `initiateUnstaking()` call made by the operator.

**Loop chain 2 — public price update path:**

`updateRSETHPrice()` (no access control, only `whenNotPaused`) → `_getTotalEthInProtocol()`:

```solidity
// LRTOracle.sol L336-348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    unchecked { ++assetIdx; }
}
```

`getTotalAssetDeposits(asset)` calls `getAssetDistributionData(asset)` for every supported asset, triggering the full NDC × queued-withdrawal nested loop for **each** supported asset. This is a triple-nested loop: `supportedAssets.length × nodeDelegatorQueue.length × queuedWithdrawals.length × strategies.length`.

---

### Impact Explanation

- **Deposit path OOG**: When the nested loop exceeds the block gas limit, every call to `depositETH()` and `depositAsset()` reverts. Users cannot deposit into the protocol. This is a **temporary freezing of funds in motion** (user deposits).
- **Price update OOG**: `updateRSETHPrice()` reverts, leaving `rsETHPrice` stale. A stale price causes mispricing of new deposits and withdrawals, and prevents protocol fee minting — constituting **temporary freezing of unclaimed yield** and potential share mis-accounting.

Impact: **Medium — Temporary freezing of funds / Unbounded gas consumption.**

---

### Likelihood Explanation

The `nodeDelegatorQueue` is admin-controlled but the protocol is designed to scale with multiple NDCs. The `queuedWithdrawals` array in EigenLayer grows with every `initiateUnstaking()` call (operator-triggered, routine operation) and shrinks only when `completeUnstaking()` is called. During periods of high unstaking activity (e.g., validator exits, operator undelegation), many withdrawals accumulate simultaneously. With even a modest number of NDCs (e.g., 5) and queued withdrawals per NDC (e.g., 20), the gas cost of the nested loop across all supported assets becomes prohibitive. This is a realistic operational scenario, not a theoretical edge case.

---

### Recommendation

1. **Paginate `getAssetDistributionData`**: Accept `from`/`to` index parameters for the NDC loop, analogous to the mitigation pattern in the reference report.
2. **Cache `getAssetUnstaking` off-chain**: Move the queued-withdrawal summation to a view function called off-chain; store a cached `assetUnstaking` value updated by the operator, rather than computing it live in every deposit and price-update call.
3. **Decouple price update from full TVL scan**: Store per-asset TVL snapshots updated incrementally rather than recomputing the full sum on every `updateRSETHPrice()` call.

---

### Proof of Concept

1. Protocol has 3 supported assets and 5 NDCs (`nodeDelegatorQueue.length = 5`).
2. Operator calls `initiateUnstaking()` repeatedly over time; each NDC accumulates 30 queued withdrawals, each with 2 strategies → 60 strategy iterations per NDC.
3. A user calls `depositETH(...)`.
4. Execution path: `_beforeDeposit` → `getTotalAssetDeposits(ETH)` → `getETHDistributionData()` → loop over 5 NDCs → each NDC calls `getAssetUnstaking(ETH)` → fetches 30 withdrawals × 2 strategies = 60 iterations per NDC → 300 total inner iterations, each with an external `DelegationManager` storage read.
5. For `updateRSETHPrice()`: the outer loop runs for 3 assets, each triggering the same 300-iteration inner loop → 900 total inner iterations plus 3 × 5 = 15 `getAssetBalance()` external calls.
6. At sufficient scale, both transactions revert with out-of-gas. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L482-493)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;

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
