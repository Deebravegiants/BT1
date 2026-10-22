# [M] MeritNFT.sol does not comply with ERC721 ,thereby breaking composibility

## Summary
Severity: Medium
Reporter: Angry_Mustache_Man
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L84-L93
Type: audit-issue

## Details
# MeritNFT.sol does not comply with ERC721 ,thereby breaking composibility

## Summary
Check Vulnerability Detail
## Vulnerability Detail
In the README it is clearly said that `The NFT contract complies with ERC721` , but under the CAVEAT section of the official documentation of the ERC721 says : 
A contract which complies with ERC-721 MUST also abide by the following:  
and describes in one of the points as : " A contract that implements ERC721Metadata or ERC721Enumerable SHALL also implement ERC721. ERC-721 implements the requirements of interface ERC-165"
which is completely missing in the `supportsInterface()` of `MeritNFT.sol`: 
```solidity 
function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(AccessControlEnumerable, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
```
## Impact
ERC721 compliant NFT might not be compatible for `MeritNFT.sol`
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L84-L93
## Tool used

Manual Review

## Recommendation
Replace present `supportinterface()` with this one:
```solidity
 function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(AccessControlEnumerable, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId) || interfaceId == type(IERC721).interfaceId ;
    }
``` 
Also inherit `IERC721`.
