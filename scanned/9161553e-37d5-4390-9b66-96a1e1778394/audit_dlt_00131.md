# [M] MerkleProof multiproofs may allow proving arbitrary leaves for specific trees

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2023-34459
Published: 2023-06-16
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-wprv-93r4-jj2p
Type: github-advisory

## Details
### Impact

When the `verifyMultiProof`, `verifyMultiProofCalldata`, `processMultiProof`, or `processMultiProofCalldata` functions are in use, it is possible to construct merkle trees that allow forging a valid multiproof for an arbitrary set of leaves.

A contract may be vulnerable if it uses multiproofs for verification and the merkle tree that is processed includes a node with value 0 at depth 1 (just under the root). This could happen inadvertently for balanced trees with 3 leaves or less, if the leaves are not hashed. This could happen deliberately if a malicious tree builder includes such a node in the tree.

A contract is not vulnerable if it uses single-leaf proving (`verify`, `verifyCalldata`, `processProof`, or `processProofCalldata`), or if it uses multiproofs with a known tree that has hashed leaves. Standard merkle trees produced or validated with the [@openzeppelin/merkle-tree](https://github.com/OpenZeppelin/merkle-tree) library are safe.

### Patches

The problem has been patched in 4.9.2

### Workarounds

If you are using multiproofs: When constructing merkle trees hash the leaves and do not insert empty nodes in your trees. Using the [@openzeppelin/merkle-tree](https://www.npmjs.com/package/@openzeppelin/merkle-tree) package eliminates this issue. Do not accept user-provided merkle roots without reconstructing at least the first level of the tree. Verify the merkle tree structure by reconstructing it from the leaves.

### Credit

0xDACA
