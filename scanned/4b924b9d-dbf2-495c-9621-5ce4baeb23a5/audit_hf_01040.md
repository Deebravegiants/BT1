# [M] Incorrect variable used in function setupNewRound()

## Summary
Severity: Medium
Contest weight: 0.5641
Dataset id: 3972
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The process of a round in AuctionV1Base is as follows:
). The operator invokes the setupNewRound() function to calculate the newPrice and start a new round. The state of the new round is set to lotteryStarted = false and winnersSelected = false.
*. The seller invokes the startLottery() function, setting the round state to lotteryStarted = true.
+. The seller calls the selectWinner() function to conclude the round and set winnersSelected = true.
In the setupNewRound() function, the numberOfTickets variable is used to determine whether the price should increase or decrease. However, numberOfTickets always resets to 0 when the previous round ends in the selectWinner() function.
```solidity
function setupNewRound(uint256 _finishAt, uint256 _numberOfTickets) public onlyOperator {
    require(_numberOfTickets <= totalNumberOfTickets, "Tickets per round cannot be higher than total number of tickets in AuctionV1");
    uint256 newPrice = 0;
    // @audit `numberOfTickets` is always reset to `0`
    // after finishing previous round in `selectWinner()`
    if (prevRoundDeposits >= numberOfTickets) {
```

## Recommendation
Consider using prevRoundTicketsAmount instead of numberOfTickets as that is kept constant after round end:
```solidity
- if (prevRoundDeposits >= numberOfTickets) {
+ if (prevRoundDeposits >= prevRoundTicketsAmount) {
```
