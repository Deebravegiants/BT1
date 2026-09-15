# [H] Users can `mint()` NFTs for the the lowest price possible (endPrice)

## Summary
Severity: High
Reporter: 33audits
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116
Type: audit-issue

## Details
# Users can `mint()` NFTs for the the lowest price possible (endPrice)

## Summary

The constructor doesn't force the start time to be before block.timestamp meaning a person can accidentally(or intentionally) create an auction with a block.timestamp in the past. This would cause the mint function to revert when attempting to calculate the timePassed or even worse allow users to mint NFTs for a lower price than the startPrice by fast forwarding timePassed [code here.](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116)

Considering in the docs, the admin is labeled as restricted without any clarity over what those restrictions are this issue is considered valid. The docs do say the "NFT contract should be set once" in this case a redeployment would be necessary and would cant the NFT contract to be set again.

## Vulnerability Detail

```solidity
        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize;
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
        return price;
```
## Impact

Let's say the contract was just deployed and the startTime was set to exactly 7 days ago instead of today while endTime was set to a week from today's date.

timePassed = Today - startTime(1 week ago) = 7 days
totalSteps = 14 (step size 1 day)
currentStep = 7 days / 1 day = 7 or the last step
priceRange = 100 - 1 = 99

price = 100 - (99 * 7 / 14) = 51

This would allow the user to then purchase the NFT for half the startPrice even though the auction just started. Essentially giving them a huge discount and causing a loss to the protocol.

## Code Snippet

Below is the code that uses the getPrice() function in order to price NFTs based on the current step.

```solidity
        uint256 pricePaid = getPrice();
        // Total price being paid is the current price times the amount of NFTs
        uint256 totalPaid = pricePaid * amount;
        // Auction must have started
        require(block.timestamp >= startTime, "Auction not started");
        // Cannot mint more than the mint cap
        require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");
        // Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
        // Make sure enough ETH was sent in the transaction
        require(msg.value >= totalPaid, "Insufficient funds");

```

You can see in the mint function that the user is required to send more ether than the total amount they've spent (`totalPaid`) so far. However `totalPaid` is being calculated by taking the amount of NFTs the user wants to mint and multiplying it by the return value of `getPrice()` which in this case would be the `endPrice` since the `startTime` was set in the past before the current block.timestamp.
 
## Tool used

Manual Review

## Recommendation

In the constructor add a require statement that forces the user to pass a startTime that is after the block.timestamp.

```solidity
require(block.timestamp <= startTime);
```
