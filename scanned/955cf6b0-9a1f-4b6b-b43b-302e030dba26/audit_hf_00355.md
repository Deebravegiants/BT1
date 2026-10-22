# [M] In the revertBatch function, in

## Summary
Severity: Medium
Contest weight: 0.6969
Dataset id: 1727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An unchecked batch reversion will cause challenge invalidation for any committed batch, leading to batch rollback issues for challengers, as the isChallenged flag will reset unexpectedly. In the revertBatch function, the inChallenge state is set to false even if the batch that was challenged is not part of the reverted batch set. This causes ongoing challenges to be incorrectly invalidated:

```solidity
function revertBatch(bytes calldata _batchHeader, uint256 _count) external onlyOwner {
    // .... REDACTED FOR BREVITY ...
    if (!challenges[_batchIndex].finished) {
        batchChallengeReward[challenges[_batchIndex].challenger] += challenges[_batchIndex].challengeDeposit;
        inChallenge = false;
    }
    // .... REDACTED FOR BREVITY ...
}
```

In the above code, `if (!challenges[_batchIndex].finished)` will hold true for challenges that don't exist. If there are no challenges for a specific `_batchIndex`, then `challenges[_batchIndex].finished` will be false which in turn makes the if condition true. This will cause `inChallenge` to be set to false even when there are ongoing challenges.

Lets assume the following batches were committed to L1 Rollup:

Batch 123  
Batch 124  
Batch 125  
Batch 126

Challenger calls `challengeState` on batch 123. This sets `isChallenged` storage variable to true.

Batch 123 (challenged)  
Batch 124  
Batch 125  
Batch 126  
isChallenged = true

While the challenge is ongoing, the owner calls `revertBatch` on Batch 125 to revert both Batch 125 and Batch 126.

Batch 123 (challenged)  
Batch 124  
Batch 125 (reverted)  
Batch 126 (reverted)  
isChallenged = true

Due to the bug in the `revertBatch` function, `isChallenged` is set to false even though the challenged batch wasn’t in the reverted batches.

Batch 123 (challenged)  
Batch 124  
isChallenged = false

This will lead to issues when the protocol is paused. Due to the following check in the `setPause` function, the challenge will not be deleted while the protocol is paused:

```solidity
function setPause(bool _status) external onlyOwner {
    // .... REDACTED FOR BREVITY ...
    // inChallenge is set to false due to the bug in revertBatch
    if (inChallenge) {
        batchChallengeReward[challenges[batchChallenged].challenger] += challenges[batchChallenged].challengeDeposit;
        delete challenges[batchChallenged];
        inChallenge = false;
    }
    // .... REDACTED FOR BREVITY ...
}
```

During the protocol pause, the prover will not be able to verify the proof and if the pause period is larger than the proof window, prover will lose the challenge and gets slashed.

Internal pre-conditions
1. Owner calls `revertBatch` on batch n, reverting the nth batch.
2. Challenger monitors the mempool and initiates a challenge on the n-1 batch.
3. Due to the bug in `revertBatch`, the `inChallenge` flag is reset to false, even though batch n-1 is under challenge.
4. Owner calls `setPause` and the protocol is paused longer than the challenge window.

External pre-conditions
None.

Attack Path
1. The owner calls `revertBatch` on batch n, reverting batch n.
2. A challenger monitors the mempool and calls `challengeBatch` on batch n-1.
3. The `revertBatch` function incorrectly resets the `inChallenge` flag to false despite batch n-1 being under challenge.
4. The protocol is paused, preventing the challenge from being deleted.
5. The prover cannot prove the batch in time due to the paused protocol.
6. The prover gets slashed, even though the batch is valid. If the protocol is paused when there's an ongoing challenge (albeit `inChallenge` is set to false due to the vulnerability explained above), the protocol slashes the batch submitter for failing to prove the batch in the challenge window, even though the batch is valid. The challenger may incorrectly receive the challenge reward + slash reward despite no actual issue in the batch.

## Recommendation
Use `batchInChallenge` function to verify the batch is indeed challenged:

```solidity
function revertBatch(bytes calldata _batchHeader, uint256 _count) external onlyOwner {
    // ... Redacted for brevity ...
    while (_count > 0) {
        emit RevertBatch(_batchIndex, _batchHash);
        committedBatches[_batchIndex] = bytes32(0);
        // if challenge exist and not finished yet, return challenge deposit to challenger
        if (batchInChallenge(_batchIndex)) {
            batchChallengeReward[challenges[_batchIndex].challenger] += challenges[_batchIndex].challengeDeposit;
            inChallenge = false;
        }
        delete challenges[_batchIndex];
        // ... Redacted for brevity ...
    }
}
```
