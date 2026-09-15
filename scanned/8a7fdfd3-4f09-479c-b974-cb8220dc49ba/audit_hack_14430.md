# [M] MeritNFT constructor lacks validation for address and string

## Summary
Severity: Medium
Reporter: V1235813
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# MeritNFT constructor lacks validation for address and string

## Summary
MeritNFT constructor lacks validation for address and string


## Vulnerability Detail

In MeritNFT constructor _name, _baseTokenURI, _symbol can be set to empty as shown in test
and
_uriSetter and _minter can be set to zero address


## Impact
Wrong values can stop the contract function to stop working


## Code Snippet
https://gist.github.com/ranevikram12/fe66747df19f55b4e3e4df9c0f4c99ea#file-gistfile1-txt-L29

 function setUp() public {
        vm.prank(owner);
      
        nft = new MeritNFT("", "", "", address(0), address(0));
    }

## Tool used
Foundry

Manual Review

## Recommendation
There must a validation for checking wrong inputs
