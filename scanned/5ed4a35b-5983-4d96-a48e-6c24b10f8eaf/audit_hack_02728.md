# [M] setAuction() does not check that current auction is in progress

## Summary
Severity: Medium
Reporter: bin2chen
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L35
Type: audit-issue

## Details
# setAuction() does not check that current auction is in progress

## Summary
when current auction is in progress or had processAuction()
if change new auction ,  there will be many exceptions, such as auction status  and all subsequent interruptions

## Vulnerability Detail

## Impact

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L35

## Tool used

Manual Review

## Recommendation

```solidity
    function setAuction(address newAuction) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newAuction != address(0), "address not provided");
        require(newAuction != address(l.Auction), "new address equals old");

        emit AuctionSet(l.epoch, address(l.Auction), newAuction, msg.sender);


+       require(l.startTime==0 || l.auctionProcessed,"bad old auction status");
        l.Auction = IAuction(newAuction);

    }
```
