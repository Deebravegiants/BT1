# [M] PirexGmx#migrateReward

## Summary
Severity: Medium
Contest weight: 0.4219
Dataset id: 17113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a reward‑loss bug that occurs during the migration of the PirexGmx contract to a new implementation. After the owner calls completeMigration, the PirexRewards contract still records the old PirexGmx address as its reward producer. The migrateReward function only transfers any remaining base reward (for example WETH) to the new contract and clears the local pirexRewards variable, but it does not update the producer field inside the external PirexRewards contract. Consequently, when an external caller – typically the AutoPxGmx contract’s compound routine – invokes PirexRewards.claim, the call is forwarded to the old PirexGmx.claimRewards function. Because the old contract is no longer authorized to distribute rewards after migration, claimRewards returns zero and the pending reward amount is effectively lost. From a user’s perspective the expected reward balance remains unchanged or appears to be zero, even though the user initiated a claim and the transaction succeeds without reverting. The impact is that users, bots, or any participant that relies on automatic reward harvesting after migration receive no reward, resulting in a silent loss of funds. The bug is triggered only after the migration sequence (completeMigration followed by migrateReward) and before the producer reference is corrected. It was discovered during a Code4rena audit by analysing the migration flow and noticing that the producer address was never reassigned. The issue is hard to notice because the claim transaction does not revert; it simply returns a zero amount, which can be mistaken for a normal “no reward” condition. The root cause is an improper state transition – the contract’s external reference to the reward producer is left stale, violating the accounting assumption that the producer always points to the active reward contract. To remediate, the migration logic should either set the PirexRewards producer to the new PirexGmx address inside completeMigration, or explicitly reset the old contract’s pirexRewards reference to address(0) in migrateReward, thereby preventing accidental calls to the obsolete claimRewards function and ensuring that reward distribution continues correctly.

## Proof of Concept
The current migration process is: `call # completemigration ()-> # migrateward ()`

After this method, the producer of PirexRewards.sol contract is still the old PirexGmx.

At this time, if `AutoPxGmx#compound ()` is called by bot:

`AutoPxGmx#compound() -> PirexRewards#.claim() -> old_PirexGmx#claimRewards()`

`Old_PirexGmx#claimRewards ()` will return zero rewards and the reward of AutopXGMX will be lost.

Old PirexGmx still can execute <https://github.com/code-423n4/2022-11-redactedcartel/blob/03b71a8d395c02324cb9fdaf92401357da5b19d1/src/PirexGmx.sol#L824-L828>

## Recommendation
There are two ways to solve the problem.

1. Set the producer of PirexRewards to the new PirexGmx in `completeMigration ()`.
2. In `#migrateReward ()`, set the old PirexGmx’s “pirexRewards” to `address(0)`, so that you can’t use the old PirexGmx to get rewards

Simply use the second, such as:
```solidity
function migrateReward() external whenPaused {
    if (msg.sender != migratedTo) revert NotMigratedTo();
    if (gmxRewardRouterV2.pendingReceivers(address(this)) != address(0))
        revert PendingMigration();

    // Transfer out any remaining base reward (ie. WETH) to the new contract
    gmxBaseReward.safeTransfer(
        migratedTo,
        gmxBaseReward.balanceOf(address(this))
    );
    pirexRewards = address(0); //*** set pirexRewards=0,Avoid claimRewards () being called by mistake.***//
}
```
