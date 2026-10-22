# [M] The RNG finish draw auction rewards are over-

## Summary
Severity: Medium
Contest weight: 0.4663
Dataset id: 22838
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rewards for finishing the draw and submitting the previously requested randomness result are slightly overpaid due to the incorrect calculation of the elapsed auction time, wrongly including the time it takes to fulfill the Witnet randomness request.
The DrawManager.finishDraw function calculates the rewards for finishing the draw, i.e., providing the previously requested randomness result, via the _computeFinishDrawReward function in lines 338-342. The calculation is based on the difference between the timestamp when the start draw auction was closed (startDrawAuction.closedAt) and the current block timestamp. Specifically, a parabolic fractional dutch auction (PFDA) is used to incentivize shorter auction durations, resulting in faster randomness submissions.
However, the requested randomness result at block X is not immediately available to be used in the finishDraw function. According to the Witnet documentation, the randomness result is available after 5-10 minutes. This time delay is currently included when determining the elapsed auction time because startDrawAuction.closedAt marks the time when the randomness request was made, not when the result was available to be submitted.
Consequently, the protocol always overpays rewards for the finish draw. Over the course of many draws, this can lead to a significant overpayment of rewards.
timing clearly outlines the timeline for the randomness auction and states that finish draw auction price will rise once the random number is available:
The RNG auction for any given draw starts at the beginning of the following draw period and must be completed within the auction duration. Following the start RNG auction, there is an “unknown” waiting period while the RNG service fulfills the request.
Once the random number is available, the finished RNG auction will rise in price until it is called to award the draw with the available random number. Once the draw is awarded for a prize pool, it will distribute the fractional reserve portions based on the auction results that contributed to the closing of that draw.
The protocol overpays rewards for the finish draw.
pt-v5-draw-manager/src/DrawManager.sol#L339
```solidity
/// @notice Called to award the prize pool and pay out rewards.
/// @param _rewardRecipient The recipient of the finish draw reward.
/// @return The awarded draw ID
function finishDraw(address _rewardRecipient) external returns (uint24) {
    if (_rewardRecipient == address(0)) {
        revert RewardRecipientIsZero();
    }

    StartDrawAuction memory startDrawAuction = getLastStartDrawAuction();
    // [...]
    (uint256 _finishDrawReward, UD2x18 finishFraction) = _computeFinishDrawReward(
        startDrawAuction.closedAt,
        block.timestamp,
        availableRewards
    );
    uint256 randomNumber = rng.randomNumber(startDrawAuction.rngRequestId);
```

## Recommendation
Consider determining the auction start for the finish draw reward calculation based on the timestamp when the randomness result was made available. This timestamp is accessible by using the WitnetRandomnessV2.fetchRandomnessAfterProof function (instead of fetchRandomnessAfter). The _witnetResultTimestamp return value can be used to better approximate the auction start, hence, paying out rewards more accurately.
