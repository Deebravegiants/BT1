# [M] A batch can be unintentionally

## Summary
Severity: Medium
Contest weight: 0.6140
Dataset id: 1734
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A batch can be unintentionally challenged during L1 reorg leading to loss of funds. The incorrect batch can be challenged during L1 reorg leading to loss of funds. Firstly the README states:
"But if there is any issue about Ethereum L1 re-org leading to financial loss, that issue is valid."
In the challengeState function, the batch that is challenged is referenced by the batchIndex.
Rollup.sol#L366-L388
```solidity
/// @dev challengeState challenges a batch by submitting a deposit.
function challengeState(uint64 batchIndex) external payable onlyChallenger nonReentrant whenNotPaused {
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
However, this poses a problem because a reorg can cause the batch present in the committedBatches[batchIndex] to change and the challenger unintentionally challenging the incorrect batch, losing the challenge and their ETH.
For instance, consider the scenario where the sequencers upload two different batches at the same batchIndex, a correct batch and an incorrect batch. The initial transaction ordering is:
1. Transaction to upload an incorrect batch at batchIndex=x
2. Transaction to upload a correct batch (it will revert, as it is already occupied) at batchIndex=x
3. Challenger calls challengeState at batchIndex=x.
An L1 reorg occurs, resulting in the new transaction ordering:
1. Transaction to upload a correct batch (it will revert, as it is already occupied) at batchIndex=x
2. Transaction to upload an incorrect batch at batchIndex=x
3. Challenger calls challengeState at batchIndex=x.
Due to the L1 reorg, the challenger will now be challenging a correct batch and will proceed to lose their challenge stake as it can be proven by the sequencer.
This issue is really similar to the Optimism reorg finding: the incorrect state root can also be challenged leading to loss of bonds.
Internal pre-conditions
1. L1 reorg
External pre-conditions
n/a
Attack Path
n/a
A batch can be unintentionally challenged leading to loss of funds for the challenger

## Recommendation
In the challengeState function, allow loading the batchHeader and verifying that the committedBatches[_batchIndex] is equal to the _batchHash as is done in the other functions such as revertBatch
```solidity
/// @dev challengeState challenges a batch by submitting a deposit.
function challengeState(bytes calldata _batchHeader) external payable onlyChallenger nonReentrant whenNotPaused {
    require(!inChallenge, "already in challenge");
    (uint256 memPtr, bytes32 _batchHash) = _loadBatchHeader(_batchHeader);
    // check batch hash
    uint256 _batchIndex = BatchHeaderCodecV0.getBatchIndex(memPtr);
    require(committedBatches[_batchIndex] == _batchHash, "incorrect batch hash");
    require(lastFinalizedBatchIndex < _batchIndex, "batch already finalized");
    require(committedBatches[_batchIndex] != 0, "batch not exist");
    require(challenges[_batchIndex].challenger == address(0), "batch already challenged");
    // check challenge window
    require(batchInsideChallengeWindow(_batchIndex), "cannot challenge batch outside the challenge window");
    // check challenge amount
    require(msg.value >= IL1Staking(l1StakingContract).challengeDeposit(), "insufficient value");
    batchChallenged = _batchIndex;
    challenges[_batchIndex] = BatchChallenge(_batchIndex, _msgSender(), msg.value, block.timestamp, false, false);
    emit ChallengeState(_batchIndex, _msgSender(), msg.value);
    for (uint256 i = lastFinalizedBatchIndex + 1; i <= lastCommittedBatchIndex; i++) {
        if (i != _batchIndex) {
            batchDataStore[i].finalizeTimestamp += proofWindow;
        }
    }
    inChallenge = true;
}
```
