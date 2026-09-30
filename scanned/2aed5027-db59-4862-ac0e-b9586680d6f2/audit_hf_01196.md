# [M] Merkle Path Veriﬁcation Can Equivocate on Depth of Proof

## Summary
Severity: Medium
Contest weight: 0.1629
Dataset id: 5198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Veriﬁcation of Merkle tree proofs only check up to proof length. Importantly, this means that proofs for leaves can verify even if the path is not of height depth. This can be problematic as it may be possible to have multiple values verify for a speciﬁc position at different heights of the path.
Take, for example, the FixedLenPoseidon2Hash DigestAlgorithm (implemented in prelude.rs#L60). The digest_leaf algorithm places the leaf element in the second to last position and the position in the last position: Consider a node at depth i with proof for leaf_val at depth i+1:
node = (default..., leaf_val, pos)
You could produce a proof of this leaf_val as the value for position pos. However, if i+1 is not max depth, then it may be possible to produce another valid proof for pos. Consider:
leaf_val = H(default..., leaf_val’, pos)
Then one could produce another accepting proof for leaf_val' at depth i+2 for pos (if pos traversal path matched up with second to last position) for node:
node = (default..., leaf_val', pos)

## Recommendation
There are a couple options that can be taken to mitigate:
• (Option 1) Enforce that all leaf nodes for successful lookups appear at max depth equals height.
• (Option 2) Set a different hashing approach for leaf nodes so that they cannot be confused for internal nodes, e.g., enforce leaves are hashed as: H("LEAF", default..., leaf, pos), and internal nodes are hashed as H("INTERNAL", ...).
