# [C] First-time raffle entries are double counted

## Summary
Severity: Critical
Contest weight: 0.4068
Dataset id: 16271
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol offers users the ability to enter a raffle. They can buy multiple tickets for a single raffle. When they enter for the first time a ticket instance is assigned for the user indicating the amount of tickets he owns. The initial amount of tickets bought is assigned directly to the user tickets struct.
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
    require(amount > 0, "Amount must be greater than zero");
    if (ticketsBought[msg.sender][raffleid].raffleID != raffleid) {
        ticketsBought[msg.sender][raffleid] = ticket(
            msg.sender,
            raffleid,
            amount
        );
    }
    spendXP(choosenRaffle.price, msg.sender);
    choosenRaffle.totalTicketsBought += amount;
    ticketsBought[msg.sender][raffleid].amount += amount;
    addJoinerToList(msg.sender, raffleid);
    emit JoinedGiveaway(msg.sender, amount, raffleid);
}
```
Varonve.md However later in the function the ticket amount is added again effectively doubling the amount of tickets the user bought, making it unfair for other users.

## Recommendation
When a user enters for the first time instantiate his amount with 0, because it is incremented after that
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
    require(amount > 0, "Amount must be greater than zero");
    if (ticketsBought[msg.sender][raffleid].raffleID != raffleid) {
        ticketsBought[msg.sender][raffleid] = ticket(
            msg.sender,
            raffleid,
            0
        );
    }
    spendXP(choosenRaffle.price, msg.sender);
    choosenRaffle.totalTicketsBought += amount;
    ticketsBought[msg.sender][raffleid].amount += amount;
    addJoinerToList(msg.sender, raffleid);
    emit JoinedGiveaway(msg.sender, amount, raffleid);
}
```
