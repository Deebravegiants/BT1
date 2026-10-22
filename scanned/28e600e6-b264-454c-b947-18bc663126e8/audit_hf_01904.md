# [M] Winning index can be selected more than once in the raffle

## Summary
Severity: Medium
Contest weight: 0.1076
Dataset id: 10488
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users join a raffle in exchange for the chance to win an NFT. To enter the raffle a user
needs to pay the ticket price after which he is minted an NFT representing his position. A user may have
for (uint256 i = 0; i < numWinners; i++) {
    // Find random winners and store them in array;
    uint256 winnerIndex = randomResults[i] % ticketOwners.length;
    winners.push(ticketOwners[winnerIndex]);
}
The problem is when they are picked. If two or more of the random results end on the same 3 digits that
would pick the same winning index more than once. This would cause a user to get 2 NFTs for one ticket.

## Recommendation
Remove the winning index from the array by making it equal to the last element from the array and the call
the pop() method to remove the last.
+ ticketOwners[winnerIndex] = ticketOwners[ticketOwners.length - 1];
+ ticketOwners.pop();
