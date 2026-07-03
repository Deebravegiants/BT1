### Title
Polynomial Gas Complexity in `updateRSETHPrice()` via Nested Loops Over Assets × NDCs × Queued Withdrawals × Strategies — (`contracts/LRTOracle.sol`)

### Summary
`LRTOracle.updateRSETHPrice()` is a publicly callable function whose gas cost scales as O(assets × NDCs × queued-withdrawals × strategies) due to nested iteration across protocol state. At protocol scale this can cause the transaction to run out of gas, permanently staling the rsETH price and breaking minting and withdrawal accounting for all users.

### Finding Description

`updateRSETHPrice()` is `public` and calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()`. [1](#0-0) 

`_getTotalEthInProtocol()` opens the first loop — one iteration per supported asset — and for each asset calls `ILRTDepositPool.getTotalAssetDeposits(asset)`: [2](#0-1) 

`getTotalAssetDeposits` delegates to `getAssetDistributionData`, which opens the second loop — one iteration per NodeDelegator — and for each NDC calls both `getAssetBalance` and `getAssetUnstaking`: [3](#0-2) 

`NodeDelegator.getAssetUnstaking` opens a **third and fourth nested loop**: it fetches all queued withdrawals from EigenLayer's `DelegationManager` and then iterates over every strategy inside each withdrawal: [4](#0-3) 

The combined call graph therefore executes:

```
for each asset (N):
  for each NDC (M):
    getAssetBalance()          ← 1 external EigenLayer call
    getAssetUnstaking()        ← 1 external EigenLayer call
      for each queued withdrawal (W):
        for each strategy (S):
          sharesToUnderlyingView()
```

Total complexity: **O(N × M × W × S)** external calls and storage reads in a single public transaction.

The protocol's own code acknowledges the scaling concern. `LRTUnstakingVault.setMaxUncompletedWithdrawalCount` contains the comment:

> *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"*

and caps the value at 80 as a buffer: [5](#0-4) 

However, `maxNodeDelegatorLimit` has **no hard cap** — the admin can raise it arbitrarily: [6](#0-5) 

As the protocol adds more supported assets, more NDCs, or more queued EigenLayer withdrawals (all of which are part of normal protocol growth), the gas cost of `updateRSETHPrice()` grows polynomially. At realistic production limits (e.g., 5 assets × 10 NDCs × 80 withdrawals × 5 strategies = 20,000 iterations, each involving external calls), the function can exceed the block gas limit.

### Impact Explanation

`rsETHPrice` is the stored value used by every deposit (`getRsETHAmountToMint`) and every withdrawal (`getExpectedAssetAmount` / `_unlockWithdrawalRequests`). If `updateRSETHPrice()` consistently reverts due to out-of-gas, the price becomes permanently stale. Users minting rsETH or completing withdrawals will receive incorrect amounts based on the last successfully stored price. This constitutes **Medium — Unbounded gas consumption** with a secondary effect of incorrect share/asset accounting for all users. [7](#0-6) [8](#0-7) 

### Likelihood Explanation

`updateRSETHPrice()` is public and permissionlessly callable. The gas cost is determined by protocol state (number of assets, NDCs, and queued EigenLayer withdrawals) that grows with normal protocol operation. No attacker action is required — the protocol reaching its own configured limits is sufficient. The team's own comment confirms they are aware the function breaks above ~120 uncompleted withdrawals, and the current cap of 80 provides only a narrow safety margin that shrinks as more assets or NDCs are added.

### Recommendation

1. **Cache `getAssetUnstaking` results**: Compute the total unstaking amount for all assets in a single pass per NDC rather than calling `getAssetUnstaking` once per (asset, NDC) pair.
2. **Decouple unstaking accounting from live EigenLayer queries**: Maintain an on-chain `assetUnstaking[asset]` accumulator updated at queue/complete time instead of re-deriving it from `getQueuedWithdrawals` on every price update.
3. **Hard-cap `maxNodeDelegatorLimit`**: Add an upper bound (e.g., 10) enforced in `updateMaxNodeDelegatorLimit` analogous to the cap on `maxUncompletedWithdrawalCount`.
4. **Separate the ETH distribution query**: `getETHDistributionData` and `getAssetDistributionData` both loop over NDCs; consolidate into a single pass.

### Proof of Concept

Call chain that triggers the nested loops:

```
updateRSETHPrice()                          // public, no auth
  → _updateRsETHPrice()
    → _getTotalEthInProtocol()
      → for each asset in supportedAssetList:          // loop 1
          getTotalAssetDeposits(asset)
            → getAssetDistributionData(asset)
              → for each NDC in nodeDelegatorQueue:    // loop 2
                  INodeDelegator(ndc).getAssetUnstaking(asset)
                    → DelegationManager.getQueuedWithdrawals(ndc)
                    → for each withdrawal:             // loop 3
                        for each strategy:             // loop 4
                            strategy.sharesToUnderlyingView(shares)
```

With 5 supported assets, 10 NDCs, 80 queued withdrawals (the current cap), and 5 strategies per withdrawal, this executes up to **100 external EigenLayer calls** plus **2,000 inner loop iterations** in a single transaction — all triggered by any unprivileged caller. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
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

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTUnstakingVault.sol (L151-158)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
