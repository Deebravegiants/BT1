# [H] Code is not production-ready

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
Similar to other discussed issues, several areas of the code suggest that the system is not production-ready. This results in narrow test scenarios that do not cover production code flow. 

#### Examples

In `MainContracts/contracts/AuctionTimeControl.sol` the following functions are commented out and replaced with same name functions that simply return True for testing purposes:

- isNotStartedAuction
- inAcceptingBidsPeriod
- inRevealingValuationPeriod
- inReceivingBidsPeriod


**code/MainContracts/contracts/AuctionTimeControl.sol:L30-L39**
```solidity
/*
// Indicates any auction has never held for a specified BondID
function isNotStartedAuction(bytes32 auctionID) public virtual override returns (bool) {
    uint256 closingTime = _auctionClosingTime[auctionID];
    return closingTime == 0;
}

// Indicates if the auctionID is in bid acceptance status
function inAcceptingBidsPeriod(bytes32 auctionID) public virtual override returns (bool) {
    uint256 closingTime = _auctionClosingTime[auctionID];
```


**code/MainContracts/contracts/AuctionTimeControl.sol:L67-L78**
```solidity
// TEST
function isNotStartedAuction(bytes32 auctionID)
    public
    virtual
    override
    returns (bool)
{
    return true;
}

// TEST
function inAcceptingBidsPeriod(bytes32 auctionID)
```

These commented-out functions contain essential functionality for the Auction contract. For example, `inRevealingValuationPeriod` is used to allow revealing of the bid price publicly:


**code/MainContracts/contracts/Auction.sol:L403-L406**
```solidity
require(
    inRevealingValuationPeriod(auctionID),
    "it is not the time to reveal the value of bids"
);
```

#### Recommendation

Remove the test functions and use the production code for testing. The tests must have full coverage of the production code to be considered complete.
