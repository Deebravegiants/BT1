# [M] Bribe.sol is not meant to handle fee-on-transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-velodrome
Published: 2022-05-30
Source: https://github.com/code-423n4/2022-05-velodrome-findings/issues/222
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-velodrome/blob/main/contracts/contracts/Bribe.sol#L50-L51
https://github.com/code-423n4/2022-05-velodrome/blob/main/contracts/contracts/Bribe.sol#L83-L90


# Vulnerability details

## Impact
Should a fee-on-transfer token be added as a reward token and deposited, the tokens will be locked in the `Bribe` contract. Voters will be unable to withdraw their rewards.

## Proof of Concept
Tokens are deposited into the `Bribe` contract using `notifyRewardAmount()`, where `amount` of tokens are transferred, then added directly to `tokenRewardsPerEpoch[token][adjustedTstamp]`:
```js
    _safeTransferFrom(token, msg.sender, address(this), amount);
    tokenRewardsPerEpoch[token][adjustedTstamp] = epochRewards + amount;
```

Tokens are transferred out of the `Bribe` contract using `deliverReward()`, which attempts to transfer `tokenRewardsPerEpoch[token][epochStart]` amount of tokens out.
```js
function deliverReward(address token, uint epochStart) external lock returns (uint) {
    require(msg.sender == gauge);
    uint rewardPerEpoch = tokenRewardsPerEpoch[token][epochStart];
    if (rewardPerEpoch > 0) {
        _safeTransfer(token, address(gauge), rewardPerEpoch);
    }
    return rewardPerEpoch;
}
```

If `token` happens to be a fee-on-transfer token, `deliverReward()` will always fail. For example:
* User calls `notifyRewardAmount()`, with `token` as token that charges a 2% fee upon any transfer, and `amount = 100`:
    * `_safeTransferFrom()` only transfers 98 tokens to the contract due to the 2% fee
    * Assuming `epochRewards = 0`, `tokenRewardsPerEpoch[token][adjustedTstamp]` becomes `100`
* Later on, when `deliverReward()` is called with the same `token` and `epochStart`:
    * `rewardPerEpoch = tokenRewardsPerEpoch[token][epochStart] = 100`
    * `_safeTransfer` attempts to transfer 100 tokens out of the contract
    * However, the contract only contains 98 tokens

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-velodrome-findings/issues/222_
