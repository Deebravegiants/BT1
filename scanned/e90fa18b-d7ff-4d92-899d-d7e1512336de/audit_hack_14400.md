# [H] always reverting of modifier onlyMinter

## Summary
Severity: High
Reporter: shtesesamoubiq
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158
Type: audit-issue

## Details
# always reverting of modifier onlyMinter

## Summary
always reverting of modifier onlyMinter
## Vulnerability Detail
In `MeritDutchAuction` anyone can call mint function that is interaction with mint function in `MeritNft`, but it has got a modifier that the function can be only ran by the role OnlyMinter.
## Impact
Alice likes the nft and she want to mint 3 nfts. When she call the `mint` function it is interacting with `MeringNFT.sol` `mint` function that can only be called by the onlyMinter role, but Alice does not have it, this will lead to always reverthing

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158
## Tool used

Manual Review

## Recommendation
remove the onlyMinter modifier
