# [M] Flawed modulo use of the amount of tickOwners.length

## Summary
Severity: Medium
Contest weight: 0.4270
Dataset id: 10492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function randomWinners() external onlyOwner {
    require(randomResultRequested == true, "Ghost: Cannot choose
        winners without having collected random numbers.");
    require(winners.length == 0, "Ghost: Winners already selected.");
    // require(_tokenIdCounter == MAX_TICKETS, "Ghost: All tickets
    must be sold.");
    require(block.timestamp >= raffleEndTime, "Ghost: Raffle time has
        not ended.");
    // Store the addresses of the random winners
    for (uint256 i = 0; i < numWinners; i++) {
        // Find random winners and store them in array
        uint256 winnerIndex = randomResults[i] % ticketOwners.length;
        winners.push(ticketOwners[winnerIndex]);
    }
    emit RaffleWon(winners);
}
```
In the randomWinners function the randomness first gets the randomResults that was fulfilled by chainlink.
Then we take the modulo of the value with the ticketOwners.length. This will result in a not-so-good
source of randomness and will also result in unfair chances depending on the index value of a ticket owner.
For instance, let us assume the ticketOwners.length is a high number like 897 and the randomness
request is a larger number 24234234234. Because the larger numbers you go, the chance that modulo will
return 0 decreases, it creates an unfair scenario for the ticket owner at the lower index values.

## Recommendation
Do not allow randomness from user-controlled values such as ticketOwners.length.
