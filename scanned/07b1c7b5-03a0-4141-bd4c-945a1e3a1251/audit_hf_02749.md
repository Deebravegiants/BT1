# [C] Unnecessary Unwrap() In PeginData::validate()

## Summary
Severity: Critical
Contest weight: 0.2633
Dataset id: 15104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A reachable panic occurs in the PeginData::validate() function, when a peg-in transaction is sent with a malformed proof. In the PeginData::validate() function, the merkle root for the block headers is calculated as: ```rust
let root = merkle.extract_matches(&mut txids, &mut idxs).unwrap();
```
The extract_matches() function returns an error in multiple scenarios. One such scenario is decoding a PeginMeta object from the Mint event which creates a valid merkle_proof: PartialMerkleTree object of the form: PartialMerkleTree { num_transactions: 0, bits: vec![], hashes: vec![] Note that even though the PartialMerkleTree object doesn't allow creating a struct with num_transactions == 0 from its constructors, it is possible to create an empty object using PartialMerkleTree::consensus_decode(&mut bytes). This is how the PeginMeta::deserialize() creates the merkle_proof. The result will be a panic due to the unwrap() on merkle.extract_matches(). Any user may trigger this function execution via the Minting contract, mint() function. Therefore, may cause arbitrary node crashes, giving the issue a high likelihood and impact.

## Recommendation
Return the error returned by the PartialMerkleTree::extract_matches() instead of unwrapping. This would ensure that no invalid merkle_proof is accepted.
