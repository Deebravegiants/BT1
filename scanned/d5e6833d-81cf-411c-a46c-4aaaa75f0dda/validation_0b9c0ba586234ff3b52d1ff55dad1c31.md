### Title
Nested Unbounded Loops in `updateRSETHPrice()` Cause Unbounded Gas Consumption, Risking Permanent Price Oracle Freeze — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary
The public `updateRSETHPrice()` function in `LRTOracle` triggers a deeply nested multi-contract loop whose gas cost grows polynomially with the number of supported assets, node delegators, and EigenLayer queued withdrawals. As the protocol scales through normal operation, this function can exceed the block gas limit, permanently preventing rsETH price updates and disrupting all deposit and withdrawal pricing.

---

### Finding Description

`LRTOracle.updateRSETHPrice()` is a public, permissionless function. It calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. The full call chain is:

```
updateRSETHPrice()                          [public, LRTOracle.sol:87]
  └─ _getTotalEthInProtocol()               [LRTOracle.sol:331-349]
       └─ for each supportedAsset (N):
            └─ getTotalAssetDeposits(asset)  [LRTDepositPool.sol:385-397]
                 └─ getAssetDistributionData(asset) [LRTDepositPool.sol:426-462]
                      └─ for each NDC (M):
                           └─ getAssetUnstaking(asset) [NodeDelegator.sol:405-427]
                                └─ getQueuedWithdrawals() → for each withdrawal (Q):
                                     └─ for each strategy (S)
```

**Exact references:**

- `_getTotalEthInProtocol()` loops over `supportedAssets` (N assets) and calls `getTotalAssetDeposits` per asset. [1](#0-0) 

- `getAssetDistributionData()` loops over `nodeDelegatorQueue` (M NDCs) and calls `getAssetUnstaking` per NDC per asset. [2](#0-1) 

- `getAssetUnstaking()` calls EigenLayer's `getQueuedWithdrawals(address(this))` and then iterates over all returned withdrawals (Q) and their strategies (S). [3](#0-2) 

The total number of external calls scales as **N × M × Q × S**. With protocol-allowed maximums of N=10 supported assets, M=10 NDCs (`maxNodeDelegatorLimit`), Q=80 queued withdrawals (`maxUncompletedWithdrawalCount`), and S=2 strategies per withdrawal, the worst-case iteration count is **10 × 10 × 80 × 2 = 16,000 external calls** in a single transaction.

The same nested loop is also triggered on every user deposit via `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits`. [4](#0-3) 

The protocol itself acknowledges this concern in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount`: *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"* — and caps the value at 80. [5](#0-4) 

However, the mitigation is incomplete: `getAssetUnstaking` queries EigenLayer's `getQueuedWithdrawals` directly, which is not bounded by the protocol's internal `uncompletedWithdrawalCount` counter. Forced undelegations from EigenLayer (e.g., operator slashing events) can spike the actual EigenLayer-side queued withdrawal count beyond what the protocol tracks, bypassing the cap.

---

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit, the rsETH price stored in `rsETHPrice` becomes permanently stale. All downstream consumers of `lrtOracle.rsETHPrice()` — including `getRsETHAmountToMint` (deposit minting), `getExpectedAssetAmount` (withdrawal sizing), and `_unlockWithdrawalRequests` (queue unlocking) — will operate on an incorrect price. This constitutes **Medium — Unbounded gas consumption**, with a secondary risk of **Medium — Temporary freezing of funds** if the stale price causes the deposit or withdrawal manager to revert on limit checks.

---

### Likelihood Explanation

The protocol is designed to operate with up to 10 NDCs and 10+ supported assets. The `maxUncompletedWithdrawalCount` is set to 80 by operators through normal protocol operation (not an attack). EigenLayer forced undelegations can temporarily push the actual queued withdrawal count above the protocol's tracked value. No attacker action is required — the gas exhaustion emerges from the protocol's own scaling. Likelihood is **Medium**.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` results off-chain** and pass them as calldata to `updateRSETHPrice()`, or restructure `getAssetUnstaking` to use a stored accounting variable rather than live EigenLayer enumeration.
2. **Decouple the price update loop** from the full NDC enumeration: maintain a running `totalAssetDeposits` mapping updated incrementally on deposit/withdrawal events rather than recomputing it on every price update.
3. **Add a gas guard** in `updateRSETHPrice()` that reverts with a descriptive error if the estimated loop count exceeds a safe threshold, preventing silent failure.
4. **Bound `getQueuedWithdrawals` iteration** in `getAssetUnstaking` to the protocol's `maxUncompletedWithdrawalCount` rather than relying on EigenLayer's unbounded return.

---

### Proof of Concept

```
Attacker/anyone calls:
  LRTOracle.updateRSETHPrice()
    → _getTotalEthInProtocol()
      → for i in [0..9] (10 supported assets):
          LRTDepositPool.getTotalAssetDeposits(asset[i])
            → getAssetDistributionData(asset[i])
              → for j in [0..9] (10 NDCs):
                  NodeDelegator[j].getAssetUnstaking(asset[i])
                    → DelegationManager.getQueuedWithdrawals(NDC[j])
                      → for k in [0..79] (80 queued withdrawals):
                          for s in [0..1] (2 strategies):
                            strategy.sharesToUnderlyingView(...)
                            // = 16,000 external calls total
                            // >> block gas limit on mainnet
  → REVERT (out of gas)
  → rsETHPrice permanently stale
``` [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
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

**File:** contracts/LRTUnstakingVault.sol (L151-156)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;
```
