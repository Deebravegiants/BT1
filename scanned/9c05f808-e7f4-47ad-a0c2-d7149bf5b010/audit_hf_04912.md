# [M] PerAddressTrancheVestingMerkleDistributor.claim

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 22831
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both the claim and initializeDistributionRecord methods of PerAddressTrancheVestingMerkleDistributor do not include the tranches when checking the Merkle proof (and do not even accept the tranches as a parameter). Both methods therefore always revert, before the function body is even entered.
We know from PerAddressTrancheVestingMerkle that the Merkle trees for this kind of distributor include the list of tranches for each address (and also because they have to be; there's no other way to specify the tranches). However, PerAddressTrancheVestingMerkleDistributor omits the tranches when checking the Merkle proofs. The Merkle proofs therefore always revert.
PerAddressTrancheVestingMerkleDistributor is completely inoperable.
Notice the lack of tranches here:
e/blob/main/contracts/packages/hardhat/contracts/claim/factory/PerAddressTrancheVestingMerkleDistributor.sol#L42-L58
```solidity
function initializeDistributionRecord(
    uint256 index, // the beneficiary's index in the merkle root
    address beneficiary, // the address that will receive tokens
    uint256 amount, // the total claimable by this beneficiary
    bytes32[] calldata merkleProof
) external validMerkleProof(keccak256(abi.encodePacked(index, beneficiary, amount)), merkleProof) {
    _initializeDistributionRecord(beneficiary, amount);
}

function claim(
    uint256 index, // the beneficiary's index in the merkle root
    address beneficiary, // the address that will receive tokens
    uint256 totalAmount, // the total claimable by this beneficiary
    bytes32[] calldata merkleProof
)
    external
    validMerkleProof(keccak256(abi.encodePacked(index, beneficiary, totalAmount)), merkleProof)
```
Contrast the code in PerAddressTrancheVestingMerkle, which checks the Merkle proof like this:
e/blob/main/contracts/packages/hardhat/contracts/claim/PerAddressTrancheVestingMerkle.sol#L45
```solidity
validMerkleProof(keccak256(abi.encodePacked(index, beneficiary, amount, abi.encode(tranches))), merkleProof)
```

## Recommendation
Add the tranches parameter to both methods and check in the Merkle proof
