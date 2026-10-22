# [C] Users will not be able to claim tokens during AngelSale and PrivateSale

## Summary
Severity: Critical
Contest weight: 0.3882
Dataset id: 10538
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimAngelSale and claimPrivateSale functions are designed to allow each specific group of
users to claim the allocated tokens for them. The MerkleProof.verify method is used to verify the
_merkleProof provided by the user and check whether he should be able to claim tokens.
```solidity
function claimAngelSale(
    uint256 _amount,
    bytes32[] calldata _merkleProof
) external {
    require(isVerified[msg.sender], "Not verified");
    bytes32 leaf = keccak256(abi.encodePacked(msg.sender, _amount));
    require(
        MerkleProof.verify(_merkleProof, merkleRoot, leaf),
        "Invalid proof!"
    );
    require(!AngelClaimed[msg.sender], "Already claimed");
    AngelClaimed[msg.sender] = true;
```
However, the merkleRoot which is used to be compared against the _merkleProof is never set and will be
with default value bytes32(0). The same applies to the privateMerkleRoot:
```solidity
bytes32 public merkleRoot;
bytes32 public privateMerkleRoot;
```
Even though the _merkleProof is generated off-chain and it might be valid, the function will still revert
with "Invalid proof!" as it will compare it to the default value. This will make it impossible for the users
to claim any amount of tokens as there is no method to set the merkleRoot and privateMerkleRoot
once the contract is deployed.

## Recommendation
Either set the two merkleRoot variables inside the constructor or create functions to set them later but
this will require additional check inside the claim function to check if the merkleRoot is set.
