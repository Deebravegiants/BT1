# [M] selectWinners() incorrectly pops eligibleParticipants

## Summary
Severity: Medium
Contest weight: 0.4429
Dataset id: 3994
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the selectWinners() function, when demand exceeds supply, only some participants in the eligibleParticipants list will receive a ticket. The function then removes the selected winners, retaining only the other participants. It achieves this by shifting the index and popping out from the back of the list.
```solidity
// Select the first `numberOfTickets` winners
for (uint256 i = 0; i < numberOfTickets; i++) {
    if (!isWinner(selectedWinner)) {
        setWinner(selectedWinner);
        emit WinnerSelected(selectedWinner);
        // Remove the winners from the participants list by shifting non-winners
        uint256 shiftIndex = 0;
        for (uint256 i = numberOfTickets; i < eligibleParticipants.length; i++) {
            eligibleParticipants[shiftIndex] = eligibleParticipants[i];
            shiftIndex++;
        }
        // @audit `eligibleParticipants.length` will decrease after pop()
        for (uint256 i = shiftIndex; i < eligibleParticipants.length; i++) {
            eligibleParticipants.pop();
        }
    }
}
```
However, the final loop that pops out elements uses i < eligibleParticipants.length as the stopping condition, even though the eligibleParticipants list is constantly updated during the process.
As a result, the eligibleParticipants.length decreases after every pop() operation, leading to incorrect function results.
For instance, let's say we have a list eligibleParticipants = [Alice, Bob] and shiftIndex = 0.
The function tries to pop out Alice and Bob.
At i = 0, Bob is popped out, making eligibleParticipants = [Alice].
At i = 1, the function breaks since eligibleParticipants.length == i == 1 now.

## Recommendation
Rather than using eligibleParticipants.length while popping out values, cache the length before the loop.
