# [H] Potential reentrancy vulnerability in MeritDutchAuction contract's mint function

## Summary
Severity: High
Reporter: 0xrobsol
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L155C1-L166C1
Type: audit-issue

## Details
# Potential reentrancy vulnerability in MeritDutchAuction contract's mint function

## Summary
Potential Reentrancy vulnerability in the mint function of the MeritDutchAuction contract.
## Vulnerability Detail
The mint function of the MeritDutchAuction contract, which allows users to mint new NFTs, does not implement a reentrancy guard. This lack of protection could allow an attacker to potentially mint more NFTs than they paid for if they are able to call the mint function recursively from a malicious NFT contract's onERC721Received callback.

## Impact
An attacker could potentially mint multiple NFTs for the price of one, which could lead to an unfair distribution of NFTs and disrupt the intended operation of the auction.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L155C1-L166C1

## Tool used

Manual Review

## Recommendation
The following attacker contract shows how the reentrancy attack could potentially be executed:

`
contract Attacker {
    MeritDutchAuction immutable private auction;

    constructor(address _auction) {
        auction = MeritDutchAuction(_auction);
    }

    function attack() public payable {
        auction.mint{value: msg.value}(1);
    }

    function onERC721Received(address, address, uint256, bytes memory) public returns(bytes4) {
        if (address(auction).balance >= auction.getPrice()) {
            auction.mint{value: auction.getPrice()}(1);
        }
        return this.onERC721Received.selector;
    }
}
`

In this contract, the onERC721Received function, which is called when an NFT is minted to the contract, attempts to mint another NFT by calling the mint function again. This results in reentrant calls to the mint function, potentially allowing the contract to mint multiple NFTs for the price of one.

To prevent reentrancy, consider using a reentrancy guard such as the one provided by OpenZeppelin's ReentrancyGuard contract. Alternatively, follow the Checks-Effects-Interactions pattern by moving the NFT minting and potential refunding to the end of the function.
