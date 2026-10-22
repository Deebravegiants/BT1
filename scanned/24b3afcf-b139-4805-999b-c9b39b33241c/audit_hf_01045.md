# [M] User can join multiple times to increase chances of winning

## Summary
Severity: Medium
Contest weight: 0.7661
Dataset id: 3996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When joining the lottery in Deposit a user would call deposit:
```solidity
function deposit() public payable whenLotteryNotActive {
    require(msg.value > 0, "No funds sent");
    if (deposits[msg.sender] == 0) {
        participants.push(msg.sender);
    }
    deposits[msg.sender] += msg.value;
}
```
Once a participant is in the participants list, if they have a large enough deposit they will be added to eligibleParticipants in checkEligibleParticipants, when the seller has called startLottery:
```solidity
function checkEligibleParticipants() internal {
    for (uint256 i = 0; i < participants.length; i++) {
        uint256 depositedAmount = deposits[participants[i]];
        if (depositedAmount >= minimumDepositAmount) {
            // Mark this participant as eligible for the lottery
            eligibleParticipants.push(participants[i]);
        }
    }
}
```
The issue here is that the buyer can add themselves multiple times to participants. The buyer can call deposit followed by withdrawDeposit then deposit again. Since withdrawing the deposit sets your deposits to 0 the second call to deposit would add them again in the participants list. This still just having paid for one deposit.
Which later would grant them multiple spots in eligibleParticipants from where the winner is picked from.
The user would still just win once since there's a check in selectWinners that they haven't won before.

## Proof of Concept
Add this test to Deposit.t.sol:
```solidity
function test_DepositJoinMultipleTimes() public {
    vm.deal(user, 1e18);
    vm.startPrank(user);
    deposit.deposit{value: 1e18}();
    deposit.buyerWithdraw();
    deposit.deposit{value: 1e18}();
    vm.stopPrank();
    assertEq(participants[0],user);
    assertEq(participants[1],user);
}
```

## Recommendation
Consider only letting buyers withdraw after the lottery has ended:
```solidity
- function buyerWithdraw() public whenLotteryNotActive {
+ function buyerWithdraw() public lotteryEnded {
```
