# [H] Participants can join knowing they'll win

## Summary
Severity: High
Contest weight: 0.7756
Dataset id: 3960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Winners are picked in LotteryV1 and AuctionV1 by the seller calling selectWinners. This selects eligibleParticipants. Given that the number of eligible participants is bigger than the number of tickets, the participants are shuffled using the randomness provided by the VRF:
```solidity
function selectWinners() external onlySeller lotteryStarted {
    require(numberOfTickets > 0, "No tickets left to allocate");
    checkEligibleParticipants();
    if (numberOfTickets >= eligibleParticipants.length) {
        // ... everyone wins
    } else {
        // Shuffle the array of participants
        for (uint j = 0; j < eligibleParticipants.length; j++) {
            uint n = j + randomNumber % (eligibleParticipants.length - j);
            ShortString temp = eligibleParticipants[n];
            eligibleParticipants[n] = eligibleParticipants[j];
            eligibleParticipants[j] = temp;
        }
        // Select the first `numberOfTickets` winners
    }
}
```
The issue is that the random number has to be provided before this is called. Since the random number is known to everyone a user can run the above algorithm and see which spots in eligibleParticipants that wins. More importantly, if the last slot would win, if the list was increased by one from them joining (or two with them joining twice and so on). Thus after randomness is selected but before selectWinners is called they can join knowing if they'll win or not. This applies to everyone, but the last one in will always have greater knowledge than all previous participants which is unfair. Since they buyer can withdraw their deposit if they don't win this exploit costs only gas for the exploiter.

## Recommendation
Consider requiring deposits to be done before the lottery starts:
```solidity
function deposit(uint256 amount) public payable lotteryStarted {
function deposit(uint256 amount) public payable lotteryNotStarted {
```
