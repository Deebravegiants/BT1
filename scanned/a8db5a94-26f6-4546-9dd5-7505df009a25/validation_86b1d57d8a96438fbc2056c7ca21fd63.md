### Title
Missing Upper Bound Validation in `setMaxNegligibleAmount` Enables Removal of NodeDelegators Holding Significant Balances - (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.setMaxNegligibleAmount` and `LRTConfig.setMaxNegligibleAmount` accept any `uint256` value with no upper bound check. The `maxNegligibleAmount` variable is the sole guard used in `_checkResidueEthBalance` and `_checkResidueLSTBalance` to prevent removal of a NodeDelegator that still holds protocol funds. If set to `type(uint256).max` (e.g., by a typo or unit error), those guards become permanently ineffective, allowing `removeNodeDelegatorContractFromQueue` to silently strand ETH and LST balances held by active NodeDelegators.

---

### Finding Description

`LRTDepositPool.setMaxNegligibleAmount` sets the threshold used by two internal guards:

```solidity
// LRTDepositPool.sol L274-277
function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
    maxNegligibleAmount = maxNegligibleAmount_;
    emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
}
```

No upper bound is enforced. The same pattern exists in `LRTConfig.setMaxNegligibleAmount` (line 256-259).

The variable is consumed in two guards inside `removeNodeDelegatorContractFromQueue`:

```solidity
// LRTDepositPool.sol L619
|| address(nodeDelegatorAddress).balance > maxNegligibleAmount
```

```solidity
// LRTDepositPool.sol L642
if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

If `maxNegligibleAmount` is set to `type(uint256).max`, both comparisons (`balance > type(uint256).max` and `assetBalance > type(uint256).max`) are always `false`. The guards never revert, and `removeNodeDelegatorContractFromQueue` succeeds regardless of how much ETH or LST the NodeDelegator holds.

The same unbounded setter in `LRTConfig` affects `removeSupportedAsset` (line 82), where `getTotalAssetDeposits(asset) > maxNegligibleAmount` would also always be false, allowing removal of an asset that still has large user deposits.

---

### Impact Explanation

Once a NodeDelegator is removed from `nodeDelegatorQueue` while holding funds:

- `isNodeDelegator[ndc] = 0` and the address is popped from the queue.
- `getTotalAssetDeposits` no longer counts those balances; protocol TVL is understated.
- Users who deposited assets routed through that NDC cannot complete withdrawals through normal protocol flows until the NDC is re-added.
- The stranded ETH/LST remains in the NDC contract but is invisible to the withdrawal manager and oracle.

This constitutes **temporary freezing of user funds** (Medium). The admin can re-add the NDC via `addNodeDelegatorContractToQueue`, but during the window the funds are inaccessible to users.

For `LRTConfig.removeSupportedAsset`, removing an asset with large deposits deletes `isSupportedAsset[asset]`, `assetStrategy[asset]`, and zeroes `depositLimitByAsset[asset]`, breaking rsETH backing accounting for all holders of that asset's deposits.

---

### Likelihood Explanation

The setter is callable only by `onlyLRTAdmin` / `DEFAULT_ADMIN_ROLE`. The scenario does not require a malicious admin — a unit error (e.g., passing `1e36` instead of `1e18`, or `type(uint256).max` as a sentinel) is a realistic honest mistake, exactly the class of error the external report describes. No attacker interaction is needed; the misconfiguration alone enables the harmful removal call.

---

### Recommendation

Add an explicit upper bound in both setters, analogous to the fix applied in the referenced UMA PR:

```solidity
// LRTDepositPool.sol
uint256 public constant MAX_NEGLIGIBLE_AMOUNT = 1 ether; // or protocol-appropriate cap

function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
    if (maxNegligibleAmount_ > MAX_NEGLIGIBLE_AMOUNT) revert ExceedsMaxNegligibleAmount();
    maxNegligibleAmount = maxNegligibleAmount_;
    emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
}
```

Apply the same cap in `LRTConfig.setMaxNegligibleAmount`.

---

### Proof of Concept

1. Admin calls `LRTDepositPool.setMaxNegligibleAmount(type(uint256).max)` — no revert, accepted unconditionally.
2. A NodeDelegator (`ndc`) holds 100 ETH and 500 stETH.
3. Admin calls `removeNodeDelegatorContractFromQueue(ndc)`.
4. `_checkResidueEthBalance`: `100 ether > type(uint256).max` → `false` → no revert.
5. `_checkResidueLSTBalance`: `500e18 > type(uint256).max` → `false` → no revert.
6. NDC is removed from `nodeDelegatorQueue`; 100 ETH + 500 stETH are stranded.
7. `getTotalAssetDeposits` no longer accounts for these balances; withdrawal manager cannot service users whose rsETH is backed by those assets. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L274-277)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```

**File:** contracts/LRTDepositPool.sol (L616-624)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L638-644)
```text
            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
```

**File:** contracts/LRTConfig.sol (L80-84)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```

**File:** contracts/LRTConfig.sol (L256-259)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```
