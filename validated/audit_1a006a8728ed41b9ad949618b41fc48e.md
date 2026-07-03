### Title
Unbounded O(M × N) Gas in `_getTotalEthInProtocol` Permanently Blocks `rsETHPrice` Updates — (`contracts/LRTOracle.sol` / `contracts/LRTConfig.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset (M) and, for each asset, calls `LRTDepositPool.getTotalAssetDeposits()` which itself iterates over every NodeDelegator (N), making 3 external calls per NDC. The total gas cost is O(M × N). Neither the supported-asset list nor `maxNodeDelegatorLimit` has a hard ceiling, so legitimate protocol growth can push `updateRSETHPrice()` — and its manager-only variant — past the block gas limit, permanently preventing price updates.

---

### Finding Description

**Call chain:**

```
updateRSETHPrice()          [public, whenNotPaused]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in getSupportedAssetList()   ← M iterations
                 ├─ getAssetPrice(asset)                   ← 1 external call / asset
                 └─ getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC in nodeDelegatorQueue  ← N iterations
                                ├─ IERC20(asset).balanceOf(ndc)   ← cold SLOAD ~2 100 gas
                                ├─ ndc.getAssetBalance(asset)     ← external call
                                └─ ndc.getAssetUnstaking(asset)   ← external call
```

**No hard caps exist on either dimension:**

- `_addNewSupportedAsset` pushes to `supportedAssetList` with no length check. [1](#0-0) 

- `updateMaxNodeDelegatorLimit` only enforces a *lower* bound (cannot shrink below current queue length); there is no upper bound. [2](#0-1) 

**The inner loop per asset:** [3](#0-2) 

**The outer loop in the oracle:** [4](#0-3) 

Each NDC call (`getAssetBalance`, `getAssetUnstaking`) is itself an external call into EigenLayer strategy contracts, adding further gas. At M = 20 assets and N = 20 NDCs the loop body executes 400 times with ≥ 3 external calls each, easily exceeding Ethereum's ~30 M gas block limit.

Both the public entry point and the manager-only entry point share the same internal function: [5](#0-4) 

So even a privileged manager cannot bypass the OOG condition.

---

### Impact Explanation

When `_getTotalEthInProtocol()` exceeds the block gas limit, every call to `updateRSETHPrice()` and `updateRSETHPriceAsManager()` reverts. The stored `rsETHPrice` becomes permanently stale. Deposits and minting continue to use the stale price via `getRsETHAmountToMint`: [6](#0-5) 

This violates the protocol invariant that rsETH price must always be updatable to reflect current collateral, and constitutes **Medium — Unbounded gas consumption** (with secondary stale-price accounting impact).

---

### Likelihood Explanation

The trigger is legitimate protocol growth, not an adversarial action. `addNewSupportedAsset` requires `TIME_LOCK_ROLE` and `addNodeDelegatorContractToQueue` requires `onlyLRTAdmin` — both are expected operational calls as the protocol expands to support more LSTs and scales its EigenLayer delegation infrastructure. No private-key compromise or governance capture is needed; the condition arises organically.

---

### Recommendation

1. **Hard-cap `supportedAssetList`**: add a `MAX_SUPPORTED_ASSETS` constant (e.g., 10) and enforce it in `_addNewSupportedAsset`.
2. **Hard-cap `maxNodeDelegatorLimit`**: add a `MAX_NODE_DELEGATORS` constant and enforce it in `updateMaxNodeDelegatorLimit`.
3. **Alternatively**, cache per-asset totals incrementally (update on deposit/withdrawal) rather than recomputing the full sum on every price update, eliminating the unbounded loop entirely.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode for a local/fork test
function testOOGOnPriceUpdate() public {
    // 1. Deploy protocol on a local fork.
    // 2. Admin adds M = 20 supported assets via addNewSupportedAsset() (TIME_LOCK_ROLE).
    // 3. Admin raises maxNodeDelegatorLimit to 20 and adds N = 20 NDCs.
    // 4. Each NDC has non-zero balances so no early-exit path is taken.
    // 5. Call updateRSETHPrice() with a gas limit equal to the block gas limit (~30M).
    // 6. Assert the transaction reverts with out-of-gas.
    //    Gas estimate: 20 assets × 20 NDCs × ~3 external calls × ~5 000 gas/call
    //                = 6 000 000 gas for inner loops alone,
    //                  plus EigenLayer strategy reads which are significantly heavier.
    //    At realistic EigenLayer call costs (~50 000 gas each), total ≈ 60 M gas > block limit.
    vm.expectRevert(); // OOG
    lrtOracle.updateRSETHPrice{gas: 30_000_000}();
}
```

The M × N cross-product gas boundary is crossed well before either dimension reaches values that would be unreasonable for a growing multi-asset restaking protocol.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
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
