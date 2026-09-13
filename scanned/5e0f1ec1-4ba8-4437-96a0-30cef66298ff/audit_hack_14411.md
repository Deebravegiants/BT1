# [M] Anyone holding `MINTER_ROLE` can mint an arbitrary of tokens exceeding `MINT_CAP` limit

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
Type: audit-issue

## Details
# Anyone holding `MINTER_ROLE` can mint an arbitrary of tokens exceeding `MINT_CAP` limit

## Summary
Anyone holding `MINTER_ROLE` can mint an arbitrary of tokens exceeding `MINT_CAP` limit
## Vulnerability Detail
The `MeritNFT` contract's `mint` function validates the caller having a `MINTER_ROLE` by the `onlyMinter` modifier.
It's not clear who can call the mint function rather than `MeritDutchAuction` contract as the info about granting of `MINTER_ROLE` is not provided. Also, it's confirmed that MeritNFT contract is deployed first.
So, it leads to the situation where the function can be called if the role is granted out of the auction contract
## Impact
Breaking of the invariants
## Code Snippet

```solidity
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63)
## Tool used

Manual Review

## Recommendation
Validate the MeritDutchAuction.minted() & mintedPerAddress[_receiver] at the call.
