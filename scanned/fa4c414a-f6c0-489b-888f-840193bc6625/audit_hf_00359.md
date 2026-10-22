# [M] Batches committed during an

## Summary
Severity: Medium
Contest weight: 0.6013
Dataset id: 1732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Batches committed during an ongoing challenge can avoid being challenged and prematurely finalize if the defender wins. After a batch is committed, there is a finalization window, in which challengers can challenge the batch's validity. After the period has elapsed, the batch can be finalized. A batch can be challenged using `challengeState()`:

```solidity
function challengeState(uint64 batchIndex) external payable onlyChallenger nonReqRevert whenNotPaused {
    require(!inChallenge, "already in challenge");
    require(lastFinalizedBatchIndex < batchIndex, "batch already finalized");
    require(committedBatches[batchIndex] != 0, "batch not exist");
    require(challenges[batchIndex].challenger == address(0), "batch already challenged");
    // check challenge window
    require(batchInsideChallengeWindow(batchIndex), "cannot challenge batch outside the challenge window");
    // check challenge amount
    require(msg.value >= IL1Staking(l1StakingContract).challengeDeposit(), "insufficient value");
    batchChallenged = batchIndex;
    challenges[batchIndex] = BatchChallenge(batchIndex, _msgSender(), msg.value, block.timestamp, false, false);
    emit ChallengeState(batchIndex, _msgSender(), msg.value);
    for (uint256 i = lastFinalizedBatchIndex + 1; i <= lastCommittedBatchIndex; i++) {
        if (i != batchIndex) {
            batchDataStore[i].finalizeTimestamp += proofWindow;
        }
    }
    inChallenge = true;
}
```

As you can see, the function loops through all the unfinalized batches, except the batch being challenged, and adds a `proofWindow` to their finalization timestamp. This is to compensate for the amount of time these batches cannot be challenged, which is the duration of the current challenge (i.e., `proofWindow`, since only one batch can be challenged at a time). However, it allows batches to get committed even when a challenge is ongoing and does not compensate for time spent during the challenge:

```solidity
batchDataStore[_batchIndex] = BatchData(
    block.timestamp,
    block.timestamp + finalizationPeriodSeconds,
    _loadL2BlockNumber(batchDataInput.chunks[_chunksLength - 1]),
    // Therefore, if the batch is successfully challenged, only the submitter will be punished.
    IL1Staking(l1StakingContract).getStakerBitmap(_msgSender()) // => batchSignature.signedSequencersBitmap
);
```

As you can see, the new batch can be finalized after `finalizationPeriodSeconds`. Currently the value of `finalizationPeriodSeconds` is 86400 (1 day) and `proofWindow` is 172800 (2 days). This means that a batch committed just after the start of a challenge will be ready to be finalized in just 1 day, before the ongoing challenge even ends.

Now, consider the following scenario:
• A batch is finalized.
• A challenger challenges this batch; the challenge will end 2 days after the start.
• A staker commits a new batch.
• After 1 day, this new batch is ready to be finalized, but can't be finalized yet as the parent batch (the challenged batch) needs to be finalized first.
• After 1.5 days, the original batch finishes its challenge: the defender wins (by providing a valid ZK proof), and the batch is ready to be finalized.
• Right after the original batch is finalized, the new batch is finalized.

This leaves no time for a challenger to challenge the new batch, and this can lead to invalid batches getting committed, even if the batch committer (sequencer) doesn't act maliciously.

Since `finalizeBatch()` is permissionless and only checks whether a batch is in the finalization window, anyone can batch the two `finalizeBatch()` calls which finalize both the original batch and the invalid batch, right after the challenge ends (by back running `proveState()`), leaving no time for a challenger to call `challengeState()`.

If a sequencer is malicious, they can easily exploit this to commit invalid batches. Critical - Can brick the entire Morph L2 protocol.

## Recommendation
You can make the following change, which correctly compensates for the lost finalization time:

```diff
batchDataStore[_batchIndex] = BatchData(
    block.timestamp,
-   block.timestamp + finalizationPeriodSeconds,
+   block.timestamp + finalizationPeriodSeconds + (inChallenge ? proofWindow - (block.timestamp - challenges[batchChallenged].startTime) : 0),
    _loadL2BlockNumber(batchDataInput.chunks[_chunksLength - 1]),
    // uploaded by rollup cannot be guaranteed.
    // Therefore, if the batch is successfully challenged, only the submitter will be punished.
    IL1Staking(l1StakingContract).getStakerBitmap(_msgSender()) // => batchSignature.signedSequencersBitmap
);
```
