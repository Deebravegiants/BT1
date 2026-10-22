# [M] startLottery() sets status for the non-existing round

## Summary
Severity: Medium
Contest weight: 0.3765
Dataset id: 3973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In AuctionV1Base, the rounds mapping uses a 0-index. This means the valid indices range from [0, roundCounter - 1]. As a result, the function startLottery() sets the lotteryStarted status for a non-existing round.
```solidity
function startLottery() public onlySeller lotteryNotStarted {
    changeLotteryState(LotteryState.ACTIVE);
    checkEligibleParticipants();
    // @audit Set status for the wrong round
    // `roundCounter` is not existed
    rounds[roundCounter].lotteryStarted = true;
}
```

## Recommendation
Consider changing the index to roundCounter - 1.
