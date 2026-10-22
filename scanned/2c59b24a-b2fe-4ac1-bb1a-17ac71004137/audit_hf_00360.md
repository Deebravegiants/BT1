# [M] Malicious challenger can brick f

## Summary
Severity: Medium
Contest weight: 0.6003
Dataset id: 1733
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious challenger can brick the delay for the finalization of batches. This is possible due to the uncapped extension of the finalization period for all unfinalized batches within the challengeState function. The challengeState function extends the finalizeTimestamp by doing an addition with the proofWindow variable (2 days) for each index (all unfinalized batches) except the challenged one, with not a single check or safeguard:
```solidity
for (uint256 i = lastFinalizedBatchIndex + 1; i <= lastCommittedBatchIndex; i++) {
    if (i != batchIndex) {
        batchDataStore[i].finalizeTimestamp += proofWindow;
    }
}
```
The permissionless proveState function allows anyone including challengers to provide a ZK-proof and immediate resolution of a challenge, setting inChallenge to false:
```solidity
// Mark challenge as finished
challenges[_batchIndex].finished = true;
inChallenge = false;
```
Attack details:
• An attack window of 15 minutes (could be longer)
  – 15 minutes = ~ 75 Ethereum blocks (12 seconds per block)
  – Challenge-prove cycle (due to inChallenge flag) => 2 blocks per cycle => 37 batches
  – Each cycle extends the finalization period for all other batches by proofWindow = 2 days (37 cycles * 2 days per cycle) means that each batch would incur an additional extension of ~74 days!
• Attackers capital: 37 ETH => while risking 1 ETH!
  – Or maybe not, because the malicious challenger could get his deposit back whenever admin pauses the contract see Rollup::L444
  – claimReward function doesn't have a whenNotPaused modifier meaning that the owner has no ability to freeze attackers funds see Rollup::L543
This combination allows an attacker to:
1. Pre-generate ZK proofs for multiple batches (32 unfinalized batch)
2. Call challengeState function - Initiate a challenge on a batch
3. Call proveState function - Immediately prove the batch in the next block
• Repeat steps 2-3 multiple times
Result: Each cycle extends the finalization period for all other batches by proofWindow (2 days), finalizeTimestamp accumulates a significant delay due to repetitive extension.
• Massive delay for unfinalized batches (uncapped delay) - Huge impact on L2 - Short-term: loss of time and money

## Recommendation
Fix the current design by implementing some of these mitigation (mainly safeguards):
• Implement a cooldown period between challenges for the same challenger address
• Cap the maximum extension of the finalization period
• Check which unfinalized batches require an extension within the loop
• Break this attack incentive? - Implement withdrawal lock period for withdrawal request to monitor any suspicious activity - Add a whenNotPaused modifier on the claimReward function, in case of exploit could freeze funds
• Ultimately restrict the ”prover” actor (mitigation from sponsor discussed in private thread).
