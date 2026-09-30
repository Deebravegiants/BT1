# [C] User can buy multiple tickets but pay only for one

## Summary
Severity: Critical
Contest weight: 0.3838
Dataset id: 16272
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocols offers users the ability to spend XP in exchange to enter a raffle. Each raffle has a ticket price and a user may buy multiple tickets for one raffle. When a user calls buyTicket there is a check that verifies the user has enough balance for the amount of tickets.
```solidity
function buyTicket(uint256 raffleid, uint256 amount)
    public
    updateXP(msg.sender)
    nonReentrant
{
    require(raffleid <= raffles.length, "Raffle ID Does not exist");
    raffle storage choosenRaffle = raffles[raffleid - 1]; // points raffle at the index (raffleid-1).
    require(block.timestamp >= choosenRaffle.startTime, "Raffle has not started");
    require(block.timestamp <= choosenRaffle.endTime, "Raffle is ended");
    require(showRewards(msg.sender) >= amount * choosenRaffle.price, "Your balance is not enough.");
    spendXP(choosenRaffle.price, msg.sender);
    choosenRaffle.totalTicketsBought += amount;
    ticketsBought[msg.sender][raffleid].amount += amount;
    addJoinerToList(msg.sender, raffleid);
    emit JoinedGiveaway(msg.sender, amount, raffleid);
}
```
Varonve.md However when a user is charged for the tickets he is charged only for one ticket.

## Recommendation
Charge users for all the tickets they buy.
```solidity
// - spendXP(choosenRaffle.price, msg.sender);
+ spendXP(choosenRaffle.price * amount, msg.sender);
```
