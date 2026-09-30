# [H] `createPromotion`

## Summary
Severity: High
Contest weight: 0.6499
Dataset id: 1331
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function createPromotion(
    address _ticket,
    IERC20 _token,
    uint216 _tokensPerEpoch,
    uint32 _startTimestamp,
    uint32 _epochDuration,
    uint8 _numberOfEpochs
) external override returns (uint256) {
    _requireTicket(_ticket);

    uint256 _nextPromotionId = _latestPromotionId + 1;
    _latestPromotionId = _nextPromotionId;

    _promotions[_nextPromotionId] = Promotion(
        msg.sender,
        _ticket,
        _token,
        _tokensPerEpoch,
        _startTimestamp,
        _epochDuration,
        _numberOfEpochs
    );

    _token.safeTransferFrom(msg.sender, address(this), _tokensPerEpoch * _numberOfEpochs);

    emit PromotionCreated(_nextPromotionId);

    return _nextPromotionId;
}
```

In the current implementation of `createPromotion()`, `_epochDuration` is allowed to be `0`.

However, when `_epochDuration = 0`, it will be impossible for users to claim the rewards, and the promotion creator won’t be able to cancel it.

## Proof of Concept
1. Alice called `createPromotion()` to create a promotion with the following parameters:

   * _token: `USDC`
   * _tokensPerEpoch: `10,000`
   * _epochDuration: `0`
   * _numberOfEpochs: `10`
2. `100,000 USDC` was transferred from Alice to the `TwabRewards` contract;
3. Users tries to `claimRewards()` but the transaction always revert at `_ticket.getAverageTotalSuppliesBetween()` -> `TwabLib.getAverageBalanceBetween()` due to div by 0.
4. Alice tries to `cancelPromotion()` to retrieve the funds, but it always reverts at `_requirePromotionActive()` since the promotion already ended.

As a result, Alice’s `100,000 USDC` is frozen in the contract.

## Recommendation
Consider adding `require(_epochDuration > 0)` in `createPromotion()`.

**[PierrickGT (PoolTogether) marked as duplicate](https://github.com/code-423n4/2021-12-pooltogether-findings/issues/106#issuecomment-993713041):**

Duplicate of <https://github.com/code-423n4/2021-12-pooltogether-findings/issues/29>

I do not consider this to be a duplicate of #29 because the warden in #29 does not mention this specific failure case. This is indeed an easy to encounter bug that can be triggered as the result of a user error or a frontend bug. Loss of all funds for the promotion would be the result.

**PierrickGT (PoolTogether) confirmed and resolved:**

Implemented the suggested require: <https://github.com/pooltogether/v4-periphery/blob/e0010b689fb170daac77af5f62abba7ca1397524/contracts/TwabRewards.sol#L126>
