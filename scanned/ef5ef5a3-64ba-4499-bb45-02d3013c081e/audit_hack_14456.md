# [M] MeritDutchAuction setNFT can be set to address zero

## Summary
Severity: Medium
Reporter: V1235813
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# MeritDutchAuction setNFT can be set to address zero

## Summary
MeritDutchAuction setNFT can be set to address zero

## Vulnerability Detail
In MeritDutchAuction function setNFT can be set to address zero

## Impact
Invalid address 

## Code Snippet

https://gist.github.com/ranevikram12/015abdf43ad160397b2e2c0b04d1f53c#file-gistfile1-txt-L64

function setUp() public {
        vm.startPrank(owner);

        startTime = block.timestamp + 1 days;
        endTime = startTime + AUCTION_DURATION;

        auction = new MeritDutchAuction(
            1,
            0,
            startTime,
            endTime,
            1
        );

// setting address to zero
        auction.setNFT(address(0));

        vm.stopPrank();
    }





 function testConstructor() public {
        assertEq(auction.startPrice(), 1);
        assertEq(auction.endPrice(), 0);
        assertEq(auction.startTime(), startTime);
        assertEq(auction.endTime(), endTime);
        assertEq(auction.stepSize(), 1);
        assertEq(address(auction.nft()), address(0));
        assertEq(auction.minted(), 0);
        assertEq(auction.totalRaised(), 0);
        assertEq(auction.owner(), owner);
    }



## Tool used
foundry

Manual Review

## Recommendation
There should be a validation for  checking for invalid address
