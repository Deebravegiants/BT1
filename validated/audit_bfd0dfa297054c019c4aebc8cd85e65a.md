### Title
`getAssetUnstaking` Ignores Beacon Chain Slashing Factor, Inflating rsETH Price After Validator Slashing — (File: contracts/NodeDelegator.sol)

---

### Summary

`NodeDelegator.getAssetUnstaking` returns raw `scaledShares` for beacon-chain ETH queued withdrawals without applying the `beaconChainSlashingFactor`. After a validator is slashed, this overstates the ETH in the protocol, inflates the rsETH price, and allows users who withdraw during the inflation window to extract more ETH than they are entitled to — at the expense of remaining rsETH holders.

---

### Finding Description

`getAssetUnstaking` in `NodeDelegator.sol` iterates over EigenLayer's queued withdrawals and, for beacon-chain ETH, returns `scaledShares` verbatim:

```solidity
uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
amount += strategyAsset == LRTConstants.ETH_TOKEN
    ? sharesToUnstake                                   // ← no slashing factor applied
    : strategy.sharesToUnderlyingView(sharesToUnstake);
``` [1](#0-0) 

In EigenLayer's slashing model (`SlashingLib`), `scaledShares = depositShares × depositScalingFactor` is stored at queue time, but the actual ETH received on completion is `scaledShares × beaconChainSlashingFactor / WAD`:

```solidity
function scaleForCompleteWithdrawal(uint256 scaledShares, uint256 slashingFactor) internal pure returns (uint256) {
    return scaledShares.mulWad(slashingFactor);
}
``` [2](#0-1) 

If slashing occurs before or after a withdrawal is queued, `beaconChainSlashingFactor < WAD`, so the actual ETH received is strictly less than `scaledShares`. `getAssetUnstaking` never reads `beaconChainSlashingFactor` and therefore overstates the pending ETH.

By contrast, `getEffectivePodShares` correctly calls `NodeDelegatorHelper.getWithdrawableShare`, which delegates to EigenLayer's `getWithdrawableShares` — a function that **does** apply the slashing factor to active shares:

```solidity
function getEffectivePodShares() external view override returns (uint256 ethStaked) {
    uint256 withdrawableShare =
        NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));
    return stakedButUnverifiedNativeETH + withdrawableShare;
}
``` [3](#0-2) 

When a withdrawal is queued after slashing:

| Component | Change |
|---|---|
| `ethStakedInEigenLayer` (`getEffectivePodShares`) | decreases by `scaledShares × slashingFactor / WAD` (correct) |
| `ethUnstakingFromEigenLayer` (`getAssetUnstaking`) | increases by `scaledShares` (incorrect) |
| **Net inflation** | `scaledShares × (1 − slashingFactor / WAD)` |

`getETHDistributionData` sums both components:

```solidity
ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
    .getAssetUnstaking(LRTConstants.ETH_TOKEN);
``` [4](#0-3) 

`getTotalAssetDeposits` adds both:

```solidity
uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + ...);
``` [5](#0-4) 

`LRTOracle._getTotalEthInProtocol` feeds this into the rsETH price calculation:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [6](#0-5) 

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [7](#0-6) 

The inflated `totalETHInProtocol` directly inflates `rsETHPrice`.

---

### Impact Explanation

**Impact: High — Theft of principal from rsETH holders.**

During the window between the slashing event and `completeUnstaking`, the rsETH price is overstated. Any user who:
1. Initiates a withdrawal at the inflated price (receiving an inflated `expectedAssetAmount`), and
2. Has their request unlocked via `unlockQueue` before `completeUnstaking` corrects the price,

receives more ETH than they are entitled to. `_calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [8](#0-7) 

If both `expectedAssetAmount` and `currentReturn` are inflated (price still inflated at unlock time), the user receives the inflated amount. When `completeUnstaking` delivers less ETH than `scaledShares`, the price drops, and the shortfall is borne by remaining rsETH holders.

---

### Likelihood Explanation

Beacon-chain validator slashing is a documented, non-negligible operational risk for any ETH staking protocol. The protocol explicitly stakes 32 ETH per validator via `stake32Eth`. The vulnerability activates automatically upon any checkpoint finalization that reduces `beaconChainSlashingFactor`. The exploitation window (slashing → `completeUnstaking`) can span days to weeks, giving ample time for a withdrawal to be initiated and unlocked at the inflated price. No privileged access is required — any rsETH holder can initiate a withdrawal.

---

### Recommendation

Apply the `beaconChainSlashingFactor` when computing the ETH value of queued beacon-chain withdrawals in `getAssetUnstaking`:

```solidity
if (strategyAsset == LRTConstants.ETH_TOKEN) {
    uint64 slashingFactor = _getEigenPodManager().beaconChainSlashingFactor(address(this));
    amount += sharesToUnstake * slashingFactor / WAD;
} else {
    amount += strategy.sharesToUnderlyingView(sharesToUnstake);
}
```

This mirrors the logic EigenLayer itself uses in `scaleForCompleteWithdrawal` and makes `getAssetUnstaking` consistent with `getEffectivePodShares`.

---

### Proof of Concept

1. Protocol has one validator: 32 ETH staked, `beaconChainSlashingFactor = WAD` (1.0).
2. Validator is slashed 12.5% on the beacon chain; checkpoint is finalized → `beaconChainSlashingFactor = 0.875 × WAD`.
3. Operator calls `initiateUnstaking` to queue the withdrawal. EigenLayer stores `scaledShares = 32e18` in the withdrawal struct.
4. **`getEffectivePodShares()`** → `0 + 0 = 0` (active shares correctly reduced to 0 after queuing).
5. **`getAssetUnstaking(ETH)`** → `32e18` (returns raw `scaledShares`, ignores slashing factor).
6. **`getTotalAssetDeposits(ETH)`** is inflated by `32e18 × (1 − 0.875) = 4e18` ETH.
7. `updateRSETHPrice()` is called → rsETH price is inflated proportionally.
8. Attacker calls `initiateWithdrawal` with their rsETH → `expectedAssetAmount` is computed at the inflated price.
9. Operator calls `unlockQueue` while price is still inflated → attacker's request is unlocked at the inflated amount.
10. Attacker calls `claim` → receives more ETH than entitled.
11. Operator calls `completeUnstaking` → only 28 ETH arrives (not 32 ETH).
12. `updateRSETHPrice()` is called → price drops; remaining rsETH holders absorb the 4 ETH shortfall.

### Citations

**File:** contracts/NodeDelegator.sol (L421-424)
```text
                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
```

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/external/eigenlayer/libraries/SlashingLib.sol (L82-84)
```text
    function scaleForCompleteWithdrawal(uint256 scaledShares, uint256 slashingFactor) internal pure returns (uint256) {
        return scaledShares.mulWad(slashingFactor);
    }
```

**File:** contracts/LRTDepositPool.sol (L394-396)
```text
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L487-489)
```text
            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
