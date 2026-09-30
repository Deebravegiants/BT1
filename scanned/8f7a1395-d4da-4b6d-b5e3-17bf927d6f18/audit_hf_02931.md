# [H] returnLoserTicketXPs uses wrong price

## Summary
Severity: High
Contest weight: 0.7553
Dataset id: 16277
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
returnLoserTicketXPs is called by the owner to return the XP for the ticket owners that didn't win the raffle:
```solidity
function returnLoserTicketXPs(uint256 id) public onlyOwner {
    uint256 index = id - 1;
    require(losersPaidBack[id] == false, "Ticket prices already paid back");
    require(raffles[index].endTime >= block.timestamp);
    uint256 valueToReturn;
    for (uint256 i = 0; i < joinedAddresses[id].length; i++) {
        if (isWinnerOf[joinedAddresses[id][i]][id] == false) {
            valueToReturn = ticketsBought[joinedAddresses[id][i]][id].amount * ((9 * raffles[id].price) / 10);
            addXP(valueToReturn, joinedAddresses[id][i]);
        } else if (isWinnerOf[joinedAddresses[id][i]][id] == true) {
            valueToReturn = (ticketsBought[joinedAddresses[id][i]][id].amount) * ((9 * raffles[id].price) / 10);
            addXP(valueToReturn, joinedAddresses[id][i]);
        }
    }
}
```
raffles uses indexes on id - 1 as seen on line 403. The issue is that later raffles[id] is used. This will cause the price from a different raffle to be used.

## Recommendation
Consider using index everywhere:
```solidity
valueToReturn = ticketsBought[joinedAddresses[id][i]][id].amount * ((9 * raffles[index].price) / 10);
addXP(valueToReturn, joinedAddresses[id][i]);
} else if (isWinnerOf[joinedAddresses[id][i]][id] == true) {
valueToReturn = (ticketsBought[joinedAddresses[id][i]][id].amount - 1) * ((9 * raffles[index].price) / 10);
```
Varonve.md
