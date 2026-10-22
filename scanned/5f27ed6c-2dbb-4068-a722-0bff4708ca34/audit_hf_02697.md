# [M] L2 Proposer Can Significantly Bias Difficulty

## Summary
Severity: Medium
Contest weight: 0.4570
Dataset id: 14632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A L2 block proposer can repeatedly rearrange transactions before proposing a block to bias difficulty.
The proposer calls the function proposeBlock() with either a transaction list or a blob if EIP-4844 has been imple-
mented. In either case the value is set by the proposer which will be recorded as meta.blobHash.
```solidity
unchecked {
    meta.difficulty = meta.blobHash ^ bytes32(block.prevrandao * b.numBlocks * block.number);
}
```
The issue occurs in that difficulty is directly based off the value meta.blobHash which can be set by the block proposer.
Furthermore, the block proposer knows the fields block.prevrandao, b.numBlocks and block.number ahead of time.
By using a guess and check method the proposer is able to heavily influence the value of meta.difficulty.
To perform the attack, the proposer will first create a transaction list and set the last transaction as a no-op with calldata
0x01. The proposer then calculates meta.difficulty using the remaining fields. If the difficulty meets some required
threshold, the proposer will accept the block. Otherwise, the proposer will increment the no-op transaction calldata to
0x02 and again check if the difficulty meets the required threshold.
The proposer will repeat the process until they have found a transaction list with the required conditions for difficulty.
There are two impacts of having a non-random difficulty. The first is that it is used to calculate meta.minTier. Thus,
a proposer can determine exactly what proof level to achieve. Second, programs on L2 may be using difficulty as a
partial form of randomness, similar to how Taiko uses difficulty to select the proof tier. A non-random difficulty allows
for manipulation of smart contracts which use difficulty as a source of randomness.

## Recommendation
It is recommended to remove the fields that may be manipulated by the proposer to bias the difficulty.
One option is to use keccak256(abi.encodePacked(block.prevrandao, b.numBlocks, block.number)). There are still
limitations to this randomness in that it is predictable from the previous epoch boundary when block.prevrandao is
set if the L1 block is known.
Proposers still have some ability to bias the difficulty, in that they may choose not to propose a block at a certain L1
block height.
Taiko
