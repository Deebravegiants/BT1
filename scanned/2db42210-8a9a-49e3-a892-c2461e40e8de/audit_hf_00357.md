# [M] Possible wrong accounting in

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 1730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Possible wrong accounting in L1Staking.sol during some slashing occasions. Stakers are permitted to commit batches in the rollup contract and these batches can be challenged by challengers. If the challenge is successful, the challenger gets part of the staker's ETH and the staker is removed; the owner also takes the rest. If it wasn't successful, the prover takes all the challengeDeposit. According to proofWindow, which is the time a challenged batch has to go without being proven for it to be successfully challenged, can be set to as high as 604800 seconds (7 days), and withdrawalLockBlocks default value is also 7 days (No relation between the two was done and owner can change proofWindow value in rollup contract). For this vulnerability we'll assume proofWindow is set to 7 days.

The issue stems from a staker being able to commit a wrong batch and still being able to withdraw from the staking contract without that batch being finalized or proven. Let's cite this example with proofWindow being set to 7 days:
• Alice, a staker, commits a wrong batch and immediately goes ahead to withdraw her ETH from the staking contract. Her 7 days period countdown starts.
• Bob, a challenger, sees that wrong batch and challenges it. Since it's a wrong batch, there's no proof for it, so a 7-day countdown starts. But remember the withdraw function's 7-day countdown started first, so when it elapses, Alice quickly withdraws her ETH.
• Then when Bob calls proveState(), Alice is supposedly slashed, but it's useless as she's already left the system.
• Then the contract is updated as though Alice's ETH is still in the contract:

```solidity
uint256 reward = (valueSum * rewardPercentage) / 100;
slashRemaining += valueSum - reward;
_transfer(rollupContract, reward);
```

So a current staker's ETH is the one being sent to the rollup contract and being assigned to the owner via `slashRemaining`. So there's less ETH than the contract is accounting for, which is already an issue. This will be detrimental when all the ETH is being withdrawn by stakers and the owner, the last person's transaction will revert because that ETH is not in the contract.

Incorrect contract accounting.

## Recommendation
Ensure stakers can't withdraw if they have a batch that is unfinalized or unproven and always ensure that withdraw time block is > proofWindow.
