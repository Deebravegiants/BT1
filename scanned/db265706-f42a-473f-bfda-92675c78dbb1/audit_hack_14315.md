# [M] CAP_PER_ADDRESS can be bypassed by minting via mutiple contracts.

## Summary
Severity: Medium
Reporter: dec3ntraliz3d
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143
Type: audit-issue

## Details
# CAP_PER_ADDRESS can be bypassed by minting via mutiple contracts.

## Summary

CAP_PER_ADDRESS can be bypassed by creating multiple contracts and minting via them.

## Vulnerability Detail

`MeritDutchAuction` contract checks and makes sure a single wallet address can't mint more than four NFTs. A wallet can bypass this by creating multiple contracts and minting via those contracts. Once the NFTs are minted, they can all be transferred to the wallet.

## Impact

NFT minting may not be fair. Bots can scoop up large amounts of NFTs.

## Code Snippet

[Link to code](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143)

```solidity
function mint(uint256 amount) external payable {
    ...
    ...
    uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
    ...
    ....
    require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
}

```


## Tool used

Manual Review

## Recommendation

My recommendation is to implement a Merkle tree with a whitelist to enforce the CAP_PER_ADDRESS restriction. The openzeppelin [Merkle Tree](https://github.com/OpenZeppelin/merkle-tree) library can be utilized for this purpose.
