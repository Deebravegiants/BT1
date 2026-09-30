# [H] Participating in raffle with multiple tickets does not work

## Summary
Severity: High
Contest weight: 0.5898
Dataset id: 10463
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol has a raffle where users can buy tickets with ETH in exchange for the chance to win an NFT from the GHOST collection. There are 1000 tickets in total and 10 winners. A user may buy multiple tickets. Chainlink VRF. After that, they can redeem their NFT using the GhostNFTMarketplace::initialSale function. If we take a look at the function it uses merkle tree verification, to verify the buyer is a winner, where the leaf function
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
```
We can also see that the claimed mapping is updated and a winner can NOT claim more than once. Having all this in mind the problem is that a user can win more than one NFT from the raffle, but can claim at most one. If a user has two or more winning tickets he could claim only 1 NFT.

## Recommendation
No recommendation
