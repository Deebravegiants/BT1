# [M] Auctioneer Cannot Be Removed From The Pro-

## Summary
Severity: Medium
Contest weight: 0.5774
Dataset id: 17768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a vulnerable Auctioneer is being exploited by an attacker, there is no way to remove the vulnerable Auctioneer from the protocol. The protocol is missing the feature to remove an auctioneer. Once an auctioneer has been added to the whitelist, it is not possible to remove the auctioneer from the whitelist.
File: BondAggregator.sol
```solidity
function registerAuctioneer(IBondAuctioneer auctioneer_) external requiresAuth {
    // Restricted to authorized addresses
    // Check that the auctioneer is not already registered
    if (_whitelist[address(auctioneer_)])
        revert Aggregator_AlreadyRegistered(address(auctioneer_));
    // Add the auctioneer to the whitelist
    auctioneers.push(auctioneer_);
    _whitelist[address(auctioneer_)] = true;
}
```
In the event that a whitelisted Auctioneer is found to be vulnerable and has been actively exploited by an attacker in the wild, the protocol needs to mitigate the issue swiftly by removing the vulnerable Auctioneer from the protocol. However, the mitigation effort will be hindered by the fact there is no way to remove an Auctioneer within the protocol once it has been whitelisted. Thus, it might not be possible to need to find a workaround to block the attack, which will introduce an unnecessary delay to the recovery process where every second counts. Additionally, if the admin accidentally whitelisted the wrong Auctioneer, there is no way to remove it.

## Recommendation
Consider implementing an additional function to allow the removal of an Auctioneer from the whitelist, so that vulnerable Auctioneer can be removed swiftly if needed.
```solidity
function deregisterAuctioneer(IBondAuctioneer auctioneer_) external requiresAuth {
    // Remove the auctioneer from the whitelist
    _whitelist[address(auctioneer_)] = false;
}
```
