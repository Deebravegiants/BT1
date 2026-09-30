# [M] `RewardsDistributor` doesn't correctly handle deposits of fee-on-transfer incentive tokens

## Summary
Severity: Medium
Contest weight: 0.4269
Dataset id: 20540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`the kenneth` stated in telegram that Fee-On-Transfer tokens are fine to use as incentive tokens with `RewardsDistributor`, however when receiving Fee-On-Transfer tokens and storing the reward amount the accounting does not account for the fee deducted from the transfer amount in-transit, for example:

```solidity
function _depositLPIncentive(
    StoredReward memory reward,
    uint256 amount,
    uint256 periodReceived
) private {
    IERC20(reward.token).safeTransferFrom(
        msg.sender,
        address(this),
        amount
    );

    // @audit stored `amount` here will be incorrect since it doesn't account for
    // the actual amount received after the transfer fee was deducted in-transit
    _storeReward(periodReceived, reward, amount);
}
```

The actual reward calculation is done off-chain and is outside the audit scope nor do we have visibility of that code. But events emitted by `RewardsDistributor` and the stored incentive token deposits in `RewardsDistributor::periodRewards` use incorrect amounts for Fee-On-Transfer incentive token deposits.

## Recommendation
In `RewardsDistributor::_depositLPIncentive` & `depositVoteIncentive`:
* read the `before` transfer token balance of `RewardsDistributor` contract
* perform the token transfer
* read the `after` transfer token balance of `RewardsDistributor` contract
* calculate the difference between the `after` and `before` balances to get the true amount that was received by the `RewardsDistributor` contract accounting for the fee that was deducted in-transit
* use the true received amount to generate events and write the received incentive token amounts to `RewardsDistributor::periodRewards`.

Also note that `RewardsDistributor::periodRewards` is never read in the contract, only written to. If it is not used by off-chain processing then consider removing it.
