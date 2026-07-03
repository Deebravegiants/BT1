Audit Report

## Title
Inactivity Leak Before `verifyWithdrawalCredentials` Causes Artificial rsETH Price Drop and Auto-Pause — (`contracts/NodeDelegator.sol`, `contracts/LRTOracle.sol`)

## Summary

`stakedButUnverifiedNativeETH` always credits exactly 32 ETH per validator, inflating `getEffectivePodShares` and therefore `highestRsethPrice` during the unverified window. When `verifyWithdrawalCredentials` is later called, the counter is decremented by the full `N × 32 ETH` while EigenLayer only awards shares equal to each validator's reduced effective balance after an inactivity leak. The resulting drop in `getEffectivePodShares` propagates into `_updateRsETHPrice`, and if the price decline exceeds `pricePercentageLimit`, the oracle auto-pauses `LRTDepositPool` and `LRTWithdrawalManager`, freezing all user deposits and withdrawals until governance manually unpauses.

## Finding Description

**Accounting inflation during the unverified window**

`stake32Eth` unconditionally increments `stakedButUnverifiedNativeETH` by 32 ETH regardless of any subsequent beacon-chain balance erosion: [1](#0-0) 

`getEffectivePodShares` sums this counter with EigenLayer's `withdrawableShare`: [2](#0-1) 

`LRTDepositPool.getETHDistributionData` feeds this directly into the protocol's total ETH accounting: [3](#0-2) 

**Price peak is set against the inflated value**

`updateRSETHPrice()` is public with no access control beyond `whenNotPaused`: [4](#0-3) 

Any call during the unverified window sets `highestRsethPrice` to a value that includes `N × 32 ETH`: [5](#0-4) 

**Verification reveals the true (lower) balance**

`verifyWithdrawalCredentials` subtracts the full `N × 32 ETH` from the counter *before* calling EigenLayer: [6](#0-5) 

EigenLayer's `eigenPod.verifyWithdrawalCredentials` awards shares based on each validator's **effective balance at proof time** (rounded down to the nearest Gwei, capped at 32 ETH). After an inactivity leak of `L` ETH per validator, EigenLayer credits only `N × (32 ETH − L)` shares. The net change in `getEffectivePodShares` is therefore `−N × L`.

**Auto-pause trigger**

After verification, the next call to `_updateRsETHPrice` computes a `newRsETHPrice` that is lower than `highestRsethPrice` by `N × L / rsethSupply`. If this difference exceeds `pricePercentageLimit × highestRsethPrice`, the oracle pauses both the deposit pool and withdrawal manager: [7](#0-6) 

**Why existing guards are insufficient**

The price-increase guard (L252–266) only prevents non-managers from setting `highestRsethPrice` to an inflated value in a single large jump; it does not prevent the manager from doing so via `updateRSETHPriceAsManager`, and it does not prevent gradual accumulation across many smaller staking batches. Once `highestRsethPrice` is set to the inflated level, the downside guard has no mechanism to distinguish a legitimate price drop from an accounting artifact caused by the unverified-to-verified transition.

## Impact Explanation

All user deposits (`LRTDepositPool.depositETH`, `depositAsset`) and all withdrawals (`LRTWithdrawalManager`) are gated by `whenNotPaused`. Once the auto-pause fires, every user's funds are frozen until governance calls `unpause()` on each contract. This is a **temporary freezing of funds**, matching the Medium scoped impact.

## Likelihood Explanation

- Inactivity leaks are a routine beacon-chain event; any period of validator downtime (client bugs, infra outages, network partitions) produces them.
- The operator **must** eventually call `verifyWithdrawalCredentials` to properly account for the ETH; this is a required normal operation, not an attack. The SECURITY.md exclusion for privileged addresses applies to adversarial use of privilege, not to required operational steps.
- `updateRSETHPrice()` is permissionless — any address can call it immediately after `verifyWithdrawalCredentials` completes, so no further operator action is needed to trigger the pause.
- The trigger condition scales with `N` (number of unverified validators) and `L` (leak per validator). With a `pricePercentageLimit` of 1% (`1e16`) and a protocol composition where ETH validators represent a large fraction of TVL, a total leak exceeding 1% of the staked ETH suffices. With a tighter `pricePercentageLimit` (e.g., 0.1%), the required leak is proportionally smaller and more easily reached.

## Recommendation

1. **Do not count `stakedButUnverifiedNativeETH` in `highestRsethPrice` comparisons.** Either exclude it from `getEffectivePodShares` for oracle purposes, or track a separate "oracle-visible" ETH total that only includes verified shares.
2. **Alternatively**, when `verifyWithdrawalCredentials` is called, read back the actual shares awarded by EigenLayer and reconcile `stakedButUnverifiedNativeETH` against the real effective balance rather than always subtracting exactly `N × 32 ETH`.
3. **At minimum**, document that `pricePercentageLimit` must be calibrated to tolerate the maximum expected inactivity-leak magnitude across all unverified validators outstanding at any one time.

## Proof of Concept

```solidity
// Preconditions:
//   pricePercentageLimit = 1e16 (1%)
//   Protocol has 10,000 ETH in LSTs (rsethSupply = 10,000e18, rsETHPrice = 1e18)
//   highestRsethPrice = 1e18

// Step 1 – operator stakes validators in batches; manager calls updateRSETHPriceAsManager
//   after each batch to stay within the 1% per-call increase limit.
//   After all batches: stakedButUnverifiedNativeETH = N * 32e18
//   highestRsethPrice reflects (10,000 + N*32) ETH / 10,000 rsETH

// Step 2 – inactivity leak: each validator loses L ETH on the beacon chain
//   (off-chain event; no on-chain state change yet)

// Step 3 – operator calls verifyWithdrawalCredentials for all N validators
//   stakedButUnverifiedNativeETH -= N * 32e18  →  0
//   EigenLayer awards N * (32 - L) ETH shares
//   getEffectivePodShares() = N * (32 - L) * 1e18

// Step 4 – anyone calls updateRSETHPrice()
//   totalETH = 10,000 + N*(32-L)
//   newRsETHPrice = totalETH / 10,000
//   diff = highestRsethPrice - newRsETHPrice = N*L / 10,000
//   if N*L > pricePercentageLimit * (10,000 + N*32):
//       → LRTDepositPool.pause() + LRTWithdrawalManager.pause()
//       → All user deposits and withdrawals frozen

// Concrete numbers: N=50 validators, L=2.1 ETH/validator (total leak = 105 ETH)
//   highestRsethPrice = (10,000 + 1,600) / 10,000 = 1.16e18
//   newRsETHPrice     = (10,000 + 1,495) / 10,000 = 1.1495e18
//   diff = 0.0105e18
//   threshold = 1e16 * 1.16e18 / 1e18 = 0.0116e18
//   0.0105 < 0.0116 → no pause (need slightly larger leak or more validators)
//
//   N=50, L=2.5 ETH/validator (total leak = 125 ETH):
//   newRsETHPrice = (10,000 + 1,475) / 10,000 = 1.1475e18
//   diff = 0.0125e18 > 0.0116e18 → isPriceDecreaseOffLimit = true → PAUSE
```

### Citations

**File:** contracts/NodeDelegator.sol (L165-166)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;
```

**File:** contracts/NodeDelegator.sol (L239-244)
```text
        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));

        eigenPod.verifyWithdrawalCredentials(
            beaconTimestamp, stateRootProof, validatorIndices, validatorFieldsProofs, validatorFields
        );
```

**File:** contracts/NodeDelegator.sol (L556-561)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
```

**File:** contracts/LRTDepositPool.sol (L487-487)
```text
            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L294-296)
```text
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```
