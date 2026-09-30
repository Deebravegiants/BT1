# [H] Torex flow created with zero address referrer

## Summary
Severity: High
Contest weight: 0.3345
Dataset id: 23037
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When flow is created with zero address referrer, the SleepPod is created for staker with zero address. All referrer rewards will be accumulated on this SleepPod and will be locked forever as the zero address cannot access or utilize these rewards.
ntracts-cloned/packages/evm-contracts/src/BoringPrograms/InitialStakingTIP.sol#L40 the code does not check if the staker is the zero address before creating a SleepPod:
• p = $.sleepPods[staker];
• if (address(p) == address(0)) { should be changed to if (address(p) == address(0) && staker != address(0)) {
Internal pre-conditions
1. userData.referrer is provided as zero address when the flow is created
External pre-conditions
1. None
Attack Path
1. User creates a flow for Torex with zero address referrer. Then Torex.onFlowCreated() is executed, followed by a callback SuperBoring.onInFlowChanged().
in/averagex-contracts-cloned/packages/evm-contracts/src/SuperBoring.sol#L245, a SleepPod is created for the zero address:
userData.referrer = address(InitialStakingTIP.getOrCreateSleepPod(sleepPodBeacon, userData.referrer));
3. All current and subsequent referrer rewards for the zero address will be accumulated in this SleepPod and locked forever.
When a user creates a flow without a referrer, a SleepPod is created for the zero address staker, locking all referrer rewards forever and causing a loss of earnings for the stakers.

## Recommendation
```diff
diff --git a/averagex-contracts-cloned/packages/evm-contracts/src/BoringPrograms/InitialStakingTIP.sol b/averagex-contracts-cloned/packages/evm-contracts/src/BoringPrograms/InitialStakingTIP.sol
index f127835..044bfbc 100644
--- a/averagex-contracts-cloned/packages/evm-contracts/src/BoringPrograms/InitialStakingTIP.sol
+++ b/averagex-contracts-cloned/packages/evm-contracts/src/BoringPrograms/InitialStakingTIP.sol
@@ -37,7 +37,7 @@ library InitialStakingTIP {
{
Storage storage $ = _getStorage();
p = $.sleepPods[staker];
-   if (address(p) == address(0)) {
+   if (address(p) == address(0) && staker != address(0)) { // Don't create a SleepPod for zero address staker
p = $.sleepPods[staker] = createSleepPod(sleepPodBeacon, staker);
}
}
```
