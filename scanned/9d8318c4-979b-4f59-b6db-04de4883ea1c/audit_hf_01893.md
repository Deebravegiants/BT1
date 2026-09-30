# [H] Direct theft of initial sale NFT

## Summary
Severity: High
Contest weight: 0.5978
Dataset id: 10470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function initialSale(
    uint256 _tokenId,
    bytes32[] calldata proof
) external payable nonReentrant {
    require(msg.value == 1 ether, "Invalid Price");
    require(_tokenId < 10, "Invalid Token Id");
    require(claimed[msg.sender] == false, "already claimed");
    claimed[msg.sender] = true;
    require(
        MerkleProof.verify(proof, merkleRoot, toBytes32(msg.sender))
        == true,
        "Invalid user"
    );
    _processInitialSale(msg.value);
    IERC721(GhostNFTAddress).safeTransferFrom(
        _ownerAddress,
        msg.sender,
        _tokenId
    );
}
```
The initialSale function is the sale of the first 10 token ID to whitelisted individuals, the problem occurs because a user can claim a token id that has already been claimed. The following can be done by inputting the _ownerAddress as the victim/ current owner of the desired token id, then the merkle proof simply verifies that the msg.sender is valid. The final part of the logic will then transfer the inputted token id from the _ownerAddress to the msg.sender even if said token id is already claimed. This is possible if the user has given approval to the contract which is expected because the user will need to give approval to list his NFT. therefore a user can steal the token id 1 which may be more valuable from an innocent victim.

## Recommendation
Validate that the token id has already been bought in the initial sale in order to stop the theft of NFT.
