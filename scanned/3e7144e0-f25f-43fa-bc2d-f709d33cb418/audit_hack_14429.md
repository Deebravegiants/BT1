# [M] Mint will revert if nft not set

## Summary
Severity: Medium
Reporter: R-Nemes
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10
Type: audit-issue

## Details
# Mint will revert if nft not set

## Summary
The `mint` function of the `MeritDutchAuction` contract reverts if the owner has not set the nft contract address.

## Vulnerability Detail
The `nft` contract address must be set after the creation of the auction contract and potentially after the auction has started. If the owner forgets or neglects to set the nft address, any calls to the `mint` function will revert, and the auction price will continue to decrease every 12 seconds.

## Impact
As a result, the Dutch auction will begin, and the price will progressively decrease every 12 seconds. This situation can lead to missed opportunities for the auction owner, as they may be unable to sell at higher prices and end up settling for lower prices.

## Code Snippet
[MeritDutchAuction.sol#L156C1-L159C10](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10)

```solidity
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```


## Tool used
Manual Review

## Recommendation
We recommend including the `nft` address in the constructor of the auction contract to ensure that the auction is always associated with an existing `nft` contract.

```solidity
    constructor(
        uint256 startPrice_,
        uint256 endPrice_,
        uint256 startTime_,
        uint256 endTime_,
        uint256 stepSize_,
		address nft_
    ) { 
        // Cannot have 0 second steps
        require(stepSize_ > 0, "Step size must be greater than 0");
        // Duration must be a multiple of step size
        require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
        // Start price must be greater than end price
        require(startPrice_ > endPrice_, "Start price must be greater than end price");

        startPrice = startPrice_;
        endPrice = endPrice_;
        startTime = startTime_;
        endTime = endTime_;
        stepSize = stepSize_;
		
        nft = MeritNFT(nft_);
    }
```
By incorporating the above recommendation, the nft contract address will always be associated with the auction, mitigating the risk of the mint function reverting due to an unset `nft` contract address.
