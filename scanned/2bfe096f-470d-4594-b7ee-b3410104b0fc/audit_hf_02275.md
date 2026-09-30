# [M] Logic Error For MaxExposure Limit Check

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are two roles of users in the Lucky Dice contract: Banker and Player. In Banker time, the users can bank/unbank certain tokens into the protocol to receive LP tokens. In Player time, the users can bet on the dice rolling result and claim the betting rewards if they bet on the correct finalNumber.
However, since the betting rewards would be 5 times the amount of the user's betting amounts, if we do not limit the user's betting amounts, the banker may face a big lost and what's more, the protocol may fail to pay the rewards to the winners.
While reviewing the betNumber() routine, we do see there are some logic checks that are in place to constrain the betAmount by checking if the banker's maxExposureRatio is exceeded (line 292 from betNumber()). However, there is a missing multiplication of 5 for the betAmount so the current limitation may not work properly in preventing above situation.
```solidity
function betNumber(bool[6] calldata numbers, uint256 amount) external payable whenNotPaused notContract nonReentrant {
    Round storage round = rounds[currentEpoch];
    require(msg.value >= feeAmount, "msg.value > feeAmount");
    require(round.status == Status.Open, "Round not Open");
    require(block.number > round.startBlock && block.number < round.lockBlock, "Round not bettable");
    require(ledger[currentEpoch][msg.sender].amount == 0, "Bet once per round");

    uint16 numberCount = 0;
    uint256 maxSingleBetAmount = 0;
    for (uint32 i = 0; i < 6; i++) {
        if (numbers[i]) {
            numberCount = numberCount + 1;
            if (round.betAmounts[i] > maxSingleBetAmount) {
                maxSingleBetAmount = round.betAmounts[i];
            }
        }
    }

    require(numberCount > 0, "numberCount > 0");
    require(amount >= minBetAmount.mul(uint256(numberCount)), "BetAmount minBetAmount * numberCount");
    require(amount <= round.maxBetAmount.mul(uint256(numberCount)), "BetAmount round.maxBetAmount * numberCount");

    if (numberCount == 1) {
        require(
            maxSingleBetAmount.add(amount).sub(round.totalAmount.sub(maxSingleBetAmount)) < bankerAmount.mul(maxExposureRatio).div(TOTAL_RATE),
            "MaxExposure Limit"
        );
    }
}
```

## Recommendation
Improved the betNumber() routine to properly check BetAmount against maxExposureRatio.
