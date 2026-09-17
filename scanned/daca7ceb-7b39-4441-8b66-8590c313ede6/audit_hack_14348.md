# [M] Because of the lack of permissions users can use another address to mint more NTFs

## Summary
Severity: Medium
Reporter: Musaka
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54
Type: audit-issue

## Details
# Because of the lack of permissions users can use another address to mint more NTFs

## Summary
User can just use another address to mint more NTFs
## Vulnerability Detail
Because there are no white lists, no permissions needed to mint, and only ETH is required, any user who wishes to mint more than the max cap (4) can just transfer the funds to another one of his addresses and mint with it. This is why NFT mint usually implement white lists and after them public auctions/mints.

## Impact
Users can mint as many NTFs as they want.

## Code Snippet
This [won't be needed](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54) since users can avoid it all together.
```jsx
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```
## Tool used

Manual Review

## Recommendation
You can implement a simple white list mechanism or use OZ's [access control](https://docs.openzeppelin.com/contracts/2.x/api/access) to make a role that will be granted only to mintes.
