# [M] Wrong and empty uri can be set by uriSetter

## Summary
Severity: Medium
Reporter: V1235813
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Wrong and empty uri can be set by uriSetter

## Summary
Wrong and empty uri can be set by uriSetter

## Vulnerability Detail
Empty and wrong uri can be set by uriSetter in MeritNFT.sol by function setBaseURI



## Impact
Nft would not show by setting wrong uri

## Code Snippet

https://gist.github.com/ranevikram12/f88bed3c125865e5fc1e4ed7612ca0cd#file-gistfile1-txt-L28

function testSetBaseURIWrong() public {
        vm.prank(uriSetter);
        nft.setBaseURI("");
        assertEq(nft.baseURI(), "");


         vm.prank(uriSetter);
        nft.setBaseURI("asd123asdxcv");
        assertEq(nft.baseURI(), "asd123asdxcv");
    }

## Tool used
Foundry

Manual Review

## Recommendation
There should be a validation for correct uri
