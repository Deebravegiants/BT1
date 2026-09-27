# [H] Underflow can lead to mint function reverting leaving NFTs stuck in contract

## Summary
Severity: High
Reporter: 33audits
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122C59-L122C59
Type: audit-issue

## Details
# Underflow can lead to mint function reverting leaving NFTs stuck in contract

## Summary

If startTime is set to a date far in the past `mint()` can underflow and lead to nfts being stuck in the contract and the `mint()` never fully executing.

Considering in the docs, the admin is labeled as restricted without any clarity over what those restrictions are this issue is considered valid. 
## Vulnerability Detail

We have already determined that the block.timestamp can be set to a date in the past and this can allow a user to manipulate the currentStep. If the currentStep is too large it will cause the price variable to underflow and increase to the maximum possible value (2^256) - 1. This would cause the `_mint()` function to revert as the price will always be greater than any user can afford and so it would render this contract useless and all of the NFTs would be stuck in the MeritNFT contract since only the auction contract can call the NFT contract. 


## Impact
NFTs will be stuck as the transaction will always revert due to underflow in the`mint()` function.

## Code Snippet
The code below is a slightly modified version of the code for simplicity's sake however the reference is here. [LINK](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122C59-L122C59)

```solidity
    uint256 timePassed = time - startTime;
    uint256 totalSteps = (endTime - startTime) / stepSize;
    uint256 currentStep = timePassed / stepSize;
    uint256 priceRange = startPrice - endPrice;

    uint256 price = startPrice - (priceRange * currentStep / totalSteps);
    return price;
    
```

As you can see above timePassed is calculated by taking the block.timestamp and subtracting it from the startTime. However, since the startTime is not required to be greater than the block.timestamp when the contract is deployed we can set a startTime to a point in history in the past allowing us to manipulate and artificially increase it.

Due to Solidity 0.8 default checked math, the subtracting `(priceRange * currentStep / totalSteps)`  from `startPrice` will cause a negative value that will generate an underflow in the unsigned integer type and lead to a transaction revert.

Calls to getPrice will revert, and since this function is used in `mint()` to calculate the current NFT price it will also cause the `mint()` process to fail. The price drop will continue to increase as time passes, making it impossible to recover from this situation and effectively bricking the contract.

This will eventually lead to a loss of funds and stuck NFTS in the contract.

This is different from the other issue reported around setting dates in the past as this one would render the contract unusable if the startTime is too far in the past while the other is related to setting the startTime to the right moment in the past so that users can mint NFTs for the `endPrice` both of these assume the deployed fat fingers the startTime when deploying the contract as they wouldn't have the incentive to do this intentionally.

## Tool used

Manual Review

## Recommendation
Force the start time to be greater or equal to block.timestamp.

```solidity
require(block.timestamp <= startTime)
```
