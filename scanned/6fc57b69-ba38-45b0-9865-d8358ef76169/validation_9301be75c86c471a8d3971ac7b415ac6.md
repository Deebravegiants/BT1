Looking at the actual call chain in the code:

**`updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → (per asset N) `getTotalAssetDeposits()` → `getAssetDistributionData()` → (per NDC M) `getAssetUnstaking()` → `getQueuedWithdrawals()` → (per withdrawal K)**

Let me verify the exact implementation details.

### Title
Unbounded Gas in `updateRSETHPrice()` via O(N × M × K) `getAssetUnstaking` Calls — (`contracts/LRTOracle.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`updateRSETHPrice()` is a public, permissionless function. Its internal call chain iterates over N supported assets × M NodeDelegators × K queued EigenLayer withdrawals per NDC, making the gas cost grow as O(N × M × K). With no hard cap on `maxUncompletedWithdrawalCount` in the code, a sufficiently large withdrawal queue can push the call above the block gas limit, temporarily preventing any price update — including the manager's `updateRSETHPriceAsManager()`, which shares the same internal path.

---

### Finding Description

**Confirmed call chain:**

1. `LRTOracle.updateRSETHPrice()` — `public`, guarded only by `whenNotPaused` [1](#0-0) 

2. → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` — loops over every supported asset (N iterations), calling `ILRTDepositPool.getTotalAssetDeposits(asset)` per asset [2](#0-1) 

3. → `LRTDepositPool.getAssetDistributionData()` — loops over every NDC (M iterations), calling `INodeDelegator.getAssetUnstaking(asset)` per NDC [3](#0-2) 

4. → `NodeDelegator.getAssetUnstaking()` — makes a fresh external call to EigenLayer's `DelegationManager.getQueuedWithdrawals(address(this))` and then iterates over every returned withdrawal (K iterations per NDC) [4](#0-3) 

**Total cost per `updateRSETHPrice()` call:**
- `getQueuedWithdrawals` external calls: **N × M** (e.g., 5 assets × 10 NDCs = 50 calls)
- Withdrawal struct iterations: **N × Σ(K_i)** ≤ **N × maxUncompletedWithdrawalCount**

`maxUncompletedWithdrawalCount` is a storage variable in `LRTUnstakingVault` with no hard cap enforced in the contract code — it is freely settable by the admin. [5](#0-4) 

`maxNodeDelegatorLimit` is initialized to 10 but is also admin-adjustable. [6](#0-5) 

**Why `updateRSETHPriceAsManager()` does not escape the problem:**
It calls the identical `_updateRsETHPrice()` internal function, so it has the same gas profile. [7](#0-6) 

---

### Impact Explanation

If `maxUncompletedWithdrawalCount` is set to a large value (e.g., 500+) and the queue is near capacity, `updateRSETHPrice()` can exceed the Ethereum block gas limit (~30 M gas). During the EigenLayer withdrawal delay window (currently 7 days on mainnet), the queue cannot be drained quickly, so the oracle price is frozen for the duration. A stale `rsETHPrice` breaks deposit minting math, withdrawal share calculations, and any downstream protocol that reads the oracle. This is a **Medium: Unbounded gas consumption** / **Medium: Temporary freezing of funds** impact.

---

### Likelihood Explanation

- `updateRSETHPrice()` is callable by any EOA — no role required.
- The withdrawal queue fills through normal operator operations (`initiateUnstaking`, `undelegate`); no attacker cooperation is needed to reach a large queue depth.
- The protocol has no on-chain guard that prevents `maxUncompletedWithdrawalCount` from being set to a value that makes the call unexecutable.
- The "permanent" framing in the question is overstated — the DoS lasts until withdrawals complete or the admin reduces the limit — but a 7-day window of a frozen oracle is a material impact.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` per NDC per price-update call.** Currently it is called N times per NDC (once per asset). A single call per NDC whose result is reused across all assets would reduce external calls from N×M to M.
2. **Introduce a hard on-chain cap** on `maxUncompletedWithdrawalCount` (e.g., `require(value <= 50)`) so the gas envelope of `updateRSETHPrice()` is provably bounded.
3. **Consider aggregating unstaking totals** in `LRTUnstakingVault` as a running counter updated on `initiateUnstaking`/`completeUnstaking`, eliminating the need to iterate EigenLayer's queue at oracle-update time entirely.

---

### Proof of Concept

```solidity
// Fork test outline (Foundry)
// 1. Deploy protocol on a mainnet fork.
// 2. Set maxUncompletedWithdrawalCount = 200 (admin tx).
// 3. Operator calls initiateUnstaking() 200 times across 10 NDCs (20 per NDC).
// 4. Measure gas of updateRSETHPrice() — expect O(N * 200) EigenLayer reads.
// 5. Increase maxUncompletedWithdrawalCount to 1000, repeat step 3 & 4.
// 6. Assert: gas(updateRSETHPrice) grows linearly with queue depth.
// 7. Assert: at some threshold, gas > block.gaslimit (30_000_000).

function testOracleGasDoS() public {
    // queue K withdrawals per NDC across M NDCs
    for (uint i; i < M; i++) {
        for (uint j; j < K; j++) {
            vm.prank(operator);
            nodeDelegators[i].initiateUnstaking(strategies, shares);
        }
    }
    uint256 gasBefore = gasleft();
    lrtOracle.updateRSETHPrice();
    uint256 gasUsed = gasBefore - gasleft();
    assertLt(gasUsed, block.gaslimit); // will fail at large K
}
```

The root cause is confirmed at:
- `NodeDelegator.getAssetUnstaking()` — fresh `getQueuedWithdrawals` call + inner loop per invocation [4](#0-3) 
- `LRTDepositPool.getAssetDistributionData()` — calls `getAssetUnstaking` once per NDC per asset [8](#0-7) 
- `LRTOracle._getTotalEthInProtocol()` — outer loop over all assets, multiplying the cost [2](#0-1)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
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

**File:** contracts/LRTUnstakingVault.sol (L39-40)
```text
    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;
```
