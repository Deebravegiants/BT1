# [H] Prover Can Censor L2 → L1 Messages

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In L2 → L1 messaging, messages are grouped and added to a Merkle tree by the prover. During finalization, the operator (coordinator) submits the Merkle root to L1, and the user SDK rebuilds the tree to which the message is added and generates a Merkle proof to claim against the root finalized on L1. However, the prover can skip messages when building the tree. Consequently, the user cannot claim the skipped message, which might result in frozen funds.

Currently, the prover is a single entity owned by Linea. Hence, this would require malice or negligence on Linea's part.
      
#### Examples


**contracts/LineaRollup.sol:L314-L315**
```solidity
_addL2MerkleRoots(_finalizationData.l2MerkleRoots, _finalizationData.l2MerkleTreesDepth);
_anchorL2MessagingBlocks(_finalizationData.l2MessagingBlocksOffsets, lastFinalizedBlock);
```

#### Recommendation

Decentralize the prover, so messages can be included by different provers.
