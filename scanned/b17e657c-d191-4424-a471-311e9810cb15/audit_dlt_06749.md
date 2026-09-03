# [M] BondNFTs can revert when transferred

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-12-tigris
Published: 2022-12-13
Source: https://github.com/code-423n4/2022-12-tigris-findings/issues/162
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-12-tigris/blob/588c84b7bb354d20cbca6034544c4faa46e6a80e/contracts/BondNFT.sol#L329


# Vulnerability details

## Impact

`BondNFT`s should be transferrable. According the the proposal and the sponsor, `BondNFT`s should could be sold and borrowed against.
The proposal for context: https://gov.tigris.trade/#/proposal/0x2f2d1d63060a4a2f2718ebf86250056d40380dc7162fb4bf5e5c0b5bee49a6f3

The current implementation limits selling/depositing to only the same day that rewards are distributed for the `tigAsset` of the bond.

The impact if no rewards are distributed in the same day: 
1. `BondNFT`s listed on open markets will not be able to fulfil the orders
2. `BondNFT`s deposited as collateral will not be release the collateral

Because other market/platforms used for selling/depositing will not call `claimGovFees` to distribute rewards, they will revert when trying to transfer the `BondNFT`.

Realistic examples could be `BondNFT`s listed on opensea.
 
Example of reasons why rewards would not be distributed in the same day:
1. Low activity from investors, rewards are distirbuted when users lock/release/extend
2. `tigAsset` is blacklisted in `BondNFT`, rewards will not be distributed in such case.


## Proof of Concept

`BondNFT` has a mechanism to update the time `tigAsset` rewards are distributed. It uses a map that points to the last timestamp rewards were distributed for `epoch[tigAsset]`. 

`distribute` function in `BondNFT`:
https://github.com/code-423n4/2022-12-tigris/blob/588c84b7bb354d20cbca6034544c4faa46e6a80e/contracts/BondNFT.sol#L221
```
    function distribute(
        address _tigAsset,
        uint _amount
    ) external {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-12-tigris-findings/issues/162_
