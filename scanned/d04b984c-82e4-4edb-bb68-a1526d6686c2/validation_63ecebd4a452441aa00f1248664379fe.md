### Title
Block Stuffing Delays `startCheckpoint`, Causing `getEffectivePodShares()` to Undercount Pod ETH and Suppress rsETH Price — (`contracts/NodeDelegator.sol`, `contracts/LRTOracle.sol`)

---

### Summary

ETH that arrives at the EigenPod via its `receive()` fallback (beacon-chain partial-withdrawal sweeps, execution-layer rewards) is tracked by EigenLayer as `NonBeaconChainETHReceived` and is **not** converted into `beaconChainETHStrategy` shares until `startCheckpoint` is called and the resulting checkpoint is fully proven. Because `NodeDelegator.getEffectivePodShares()` reads only EigenLayer's `DelegationManager.getWithdrawableShares()` for the beacon-chain strategy, that ETH is invisible to the protocol's TVL calculation until a checkpoint is finalized. `startCheckpoint` is gated behind `onlyLRTOperator`, so an attacker who block-stuffs to prevent the operator's transaction from landing can hold the price suppressed for as long as the stuffing is sustained.

---

### Finding Description

**Step 1 — ETH lands in the EigenPod but is not yet shares.**

Beacon-chain partial-withdrawal sweeps and execution-layer rewards are sent directly to the EigenPod contract's `receive()` fallback. EigenLayer emits `NonBeaconChainETHReceived` but does **not** credit `beaconChainETHStrategy` shares until `startCheckpoint` → `verifyCheckpointProofs` → checkpoint finalization.

**Step 2 — `getEffectivePodShares()` misses this ETH.**

`NodeDelegator.getEffectivePodShares()` returns:

```
stakedButUnverifiedNativeETH + NodeDelegatorHelper.getWithdrawableShare(…beaconChainETHStrategy)
``` [1](#0-0) 

`getWithdrawableShare` delegates to `DelegationManager.getWithdrawableShares()`, which reflects only finalized checkpoint shares — not raw ETH sitting in the pod. [2](#0-1) 

**Step 3 — The gap propagates to TVL and rsETH price.**

`LRTDepositPool.getETHDistributionData()` sums `getEffectivePodShares()` as `ethStakedInEigenLayer`: [3](#0-2) 

`LRTOracle._updateRsETHPrice()` derives `totalETHInProtocol` from `getTotalAssetDeposits`, which calls `getETHDistributionData()`. The uncheckpointed pod ETH is therefore absent from the denominator of the rsETH price calculation: [4](#0-3) 

**Step 4 — `startCheckpoint` is operator-only; block stuffing blocks it.**

The only in-scope entry point to trigger a checkpoint is:

```solidity
function startCheckpoint(bool revertIfNoBalance) external onlyLRTOperator {
    eigenPod.startCheckpoint(revertIfNoBalance);
}
``` [5](#0-4) 

An attacker who fills every block with high-gas transactions can prevent the operator's `startCheckpoint` call from landing. During this window the pod's raw ETH balance is not reflected in `getEffectivePodShares()`, so `rsETHPrice` is lower than the true per-token backing.

---

### Impact Explanation

While block stuffing is active:

- `rsETHPrice` is set below the true backing (uncheckpointed pod ETH is excluded from TVL).
- New depositors minting rsETH at the suppressed price receive more rsETH per ETH than they should, diluting existing holders.
- When stuffing ends and the checkpoint is eventually finalized, `_updateRsETHPrice()` may hit the `PriceAboveDailyThreshold` guard (if the jump exceeds `pricePercentageLimit`), requiring a manager call to push the price through — further delaying correct price discovery. [6](#0-5) 

Impact: **Low — Contract fails to deliver promised returns / Block stuffing** (yield not captured in rsETH price during the stuffing window; existing holders are diluted).

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but economically rational if the attacker can profit from minting rsETH at a suppressed price and redeeming after the price corrects. The structural gap (uncheckpointed pod ETH invisible to TVL) is permanent and requires no special preconditions beyond ETH accruing to the pod — which happens continuously via beacon-chain rewards. The operator has no on-chain mechanism to bypass the block-stuffing; they can only wait or use a private mempool relay.

---

### Recommendation

1. **Include the EigenPod's raw ETH balance in `getEffectivePodShares()`**: add `address(eigenPod).balance` (minus `withdrawableRestakedExecutionLayerGwei` already counted as shares) to the return value so uncheckpointed ETH is always reflected in TVL.
2. **Alternatively**, expose a view that reads `IEigenPod.currentCheckpoint().podBalanceGwei` and adds it to the share count when a checkpoint is in progress.
3. Use a private/protected mempool relay (e.g., Flashbots `eth_sendPrivateTransaction`) for the operator's `startCheckpoint` call to make block stuffing ineffective.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// Fork test (Hardhat/Foundry, mainnet fork)
// 1. Deploy/fork the protocol with an active NodeDelegator + EigenPod.
// 2. Send 1 ETH directly to eigenPod (simulating a beacon-chain partial withdrawal):
//    vm.deal(address(eigenPod), address(eigenPod).balance + 1 ether);
// 3. Assert getEffectivePodShares() does NOT include the 1 ETH:
//    uint256 shares = nodeDelegator.getEffectivePodShares();
//    // shares does not reflect the 1 ETH sitting in eigenPod
// 4. Call LRTOracle.updateRSETHPrice() and record rsETHPrice_before.
// 5. Now call startCheckpoint + verifyCheckpointProofs (as operator) to finalize.
// 6. Call LRTOracle.updateRSETHPrice() and record rsETHPrice_after.
// 7. Assert rsETHPrice_after > rsETHPrice_before — proving the price was suppressed
//    while the ETH was uncheckpointed.
//
// Block-stuffing simulation: skip steps 5-6 and show that rsETHPrice remains
// suppressed indefinitely as long as startCheckpoint is not called.
```

### Citations

**File:** contracts/NodeDelegator.sol (L259-261)
```text
    function startCheckpoint(bool revertIfNoBalance) external onlyLRTOperator {
        eigenPod.startCheckpoint(revertIfNoBalance);
    }
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

**File:** contracts/NodeDelegatorHelper.sol (L52-65)
```text
    function getWithdrawableShare(
        ILRTConfig lrtConfig,
        IStrategy strategy
    )
        internal
        view
        returns (uint256 withdrawableShare)
    {
        IStrategy[] memory strategies = new IStrategy[](1);
        strategies[0] = strategy;

        uint256[] memory withdrawableShares = getWithdrawableShares(lrtConfig, strategies);
        return withdrawableShares[0];
    }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
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

**File:** contracts/LRTOracle.sol (L231-250)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```
