# [M] Refunds for losing tickets aren't registered

## Summary
Severity: Medium
Contest weight: 0.5409
Dataset id: 16281
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users buy tickets for a raffle and don't win, 90 % of the loosing tickets value is paid back to users in the form of XP. This is done be calling the returnLoserTicketXPs function. The function checks if the losing tickets for the raffle are already paid and if they are the transaction reverts.
```solidity
require(losersPaidBack[id] == false, "Ticket prices already paid back");
```
Varonve.md The problem is that the losersPaidBack is never set to true when the refund is done.

## Recommendation
Set losersPaidBack to true when they are repaid:
```solidity
function returnLoserTicketXPs(uint256 id) public onlyOwner {
    for (uint256 i = 0; i < joinedAddresses[id].length; i++) {
        //
    }
    losersPaidBack[id] = true;
}
```
