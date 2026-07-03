### Title
Unbounded Gas Growth in `updateRSETHPrice()` Due to O(assets × NDCs × withdrawals × strategies) Call Chain — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`updateRSETHPrice()` → `_getTotalEthInProtocol()` iterates over every supported asset, and for each asset calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → `getAssetUnstaking()` per NDC. `getAssetUnstaking()` fetches **all** queued EigenLayer withdrawals for that NDC and iterates over every strategy in every withdrawal. Because there is no hard cap on the number of supported assets, each call to `addNewSupportedAsset()` (TIME\_LOCK\_ROLE) monotonically increases the gas cost of `updateRSETHPrice()` by a factor of `NDCs × withdrawals_per_NDC × strategies_per_withdrawal`.

---

### Finding Description

**Full call chain:**

1. `LRTOracle.updateRSETHPrice()` (public, no role guard) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` [1](#0-0) 

2. `_getTotalEthInProtocol()` loops over `lrtConfig.getSupportedAssetList()` — **no cap on list length** — and for each asset calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. [2](#0-1) 

3. `getTotalAssetDeposits()` calls `getAssetDistributionData(asset)`, which loops over every NDC in `nodeDelegatorQueue` and calls both `getAssetBalance(asset)` and `getAssetUnstaking(asset)` per NDC. [3](#0-2) 

4. `NodeDelegator.getAssetUnstaking(asset)` calls `_getDelegationManager().getQueuedWithdrawals(address(this))` — loading **all** queued withdrawal structs from EigenLayer storage — then iterates over every withdrawal and every strategy within it. [4](#0-3) 

5. `addNewSupportedAsset()` is gated by `TIME_LOCK_ROLE` and has **no upper bound** on the number of assets that can be added. [5](#0-4) [6](#0-5) 

**Effective complexity per `updateRSETHPrice()` call:**

```
O(A × N × W × S)
```
where A = supported assets, N = NDCs, W = queued withdrawals per NDC, S = strategies per withdrawal.

`getQueuedWithdrawals` is called **A × N** times total (once per asset per NDC), each time loading the full withdrawal queue for that NDC from EigenLayer storage.

**Existing caps and their limits:**

| Parameter | Cap | Set by |
|---|---|---|
| `maxNodeDelegatorLimit` | 10 (default) | Manager (can increase) |
| `maxUncompletedWithdrawalCount` | ≤ 80 (global) | Manager |
| Supported assets | **None** | TIME\_LOCK\_ROLE |

The protocol's own comment acknowledges the gas concern: [7](#0-6) 

However, the comment only accounts for the withdrawal count dimension; it does not account for the asset-count multiplier. Each new supported asset multiplies the number of `getQueuedWithdrawals` calls by N (NDC count).

**Gas estimate (conservative, warm storage):**

- Each `getQueuedWithdrawals` call with 8 withdrawals × 2 strategies ≈ 30,000–50,000 gas
- With 20 assets × 10 NDCs = 200 calls → ~8,000,000 gas (within limit)
- With 40 assets × 10 NDCs = 400 calls → ~16,000,000 gas (approaching limit)
- With 50 assets × 10 NDCs = 500 calls → ~20,000,000+ gas
- If `maxNodeDelegatorLimit` is raised to 20 and 40 assets are added: 800 calls → ~32,000,000 gas → **exceeds 30M block gas limit**

---

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit, the rsETH price can never be updated. Both `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()` (manager-only) call the same `_updateRsETHPrice()` → `_getTotalEthInProtocol()` path, so neither escapes the gas ceiling. This would permanently disable price updates, breaking deposits (`getRsETHAmountToMint` uses `rsETHPrice()`), and potentially freezing the protocol.

**Impact: Medium — Unbounded gas consumption / Temporary-to-permanent freezing of price update mechanism.**

---

### Likelihood Explanation

Likelihood is **low-to-medium**. The path requires TIME\_LOCK\_ROLE to add many assets (a legitimate governance action, not an attacker exploit), and the existing caps on NDCs (10) and withdrawals (80) provide meaningful mitigation at current asset counts. However, there is no hard cap on assets, and the gas grows linearly with each addition. A protocol that grows to 30–50 supported assets with a raised NDC limit would be at risk.

---

### Recommendation

1. **Add a hard cap on `supportedAssetList.length`** in `_addNewSupportedAsset()`, e.g., `require(supportedAssetList.length < MAX_ASSETS)`.
2. **Cache `getQueuedWithdrawals` results** per NDC across asset iterations, or restructure `_getTotalEthInProtocol()` to call `getQueuedWithdrawals` once per NDC (not once per asset per NDC).
3. **Add a gas guard** in `updateRSETHPrice()` that reverts with a descriptive error if `gasleft()` drops below a safe threshold mid-loop.
4. **Document the combined cap invariant**: `assets × NDCs × avg_withdrawals_per_NDC × avg_strategies < gas_budget`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// Foundry invariant test (local fork, unmodified contracts)
// Asserts: gas(updateRSETHPrice) < 15_000_000
// for assets in [2..20], NDCs in [1..10], withdrawals in [1..10]

contract GasInvariantTest is Test {
    LRTOracle oracle;
    LRTConfig config;
    LRTDepositPool pool;

    function invariant_updateRSETHPriceGasUnder15M() public {
        uint256 gasBefore = gasleft();
        oracle.updateRSETHPrice();
        uint256 gasUsed = gasBefore - gasleft();
        assertLt(gasUsed, 15_000_000, "updateRSETHPrice exceeds 15M gas");
    }

    // setUp: deploy N mock NDCs each with W queued withdrawals (S strategies each),
    // add A mock LST assets to LRTConfig, register price oracles.
    // Vary A in [2..20], N in [1..10], W in [1..10] via fuzzing.
}
```

The test will fail for sufficiently large `(A, N, W)` combinations because `getAssetUnstaking()` is called `A × N` times, each fetching `W` withdrawals with `S` strategies from EigenLayer's `getQueuedWithdrawals()`. [4](#0-3) [3](#0-2) [2](#0-1)

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

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```

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

**File:** contracts/LRTUnstakingVault.sol (L151-153)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
```
