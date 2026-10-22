# [M] Timely _updatePool() In Multiple Routines

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 11771
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BSCStation Start Pools protocol provides an incentive mechanism that rewards the staking of the speciﬁed stakedToken assets with several kinds of ERC20 tokens speciﬁed by the rewardTokens array. The staking users are rewarded in proportional to their stakedToken assets in the pool. The new reward token can be dynamically added via the addRewardToken() routine and the reward rate (per block) of each token in the rewardTokens array can be adjusted via the updateRewardPerBlock() routine. When analyzing these two routines, we notice the lack of timely invoking _updatePool() to update the accTokenPerShare and lastRewardBlock variables before the new reward-related conﬁguration becomes eﬀective. If the call to _updatePool() is not immediately invoked before adding the new reward token or updating the reward rate, certain situations may be crafted to create an unfair reward distribution. With that, we suggest to timely invoke the _updatePool() at the beginning of these two routines.

```solidity
function addRewardToken(ERC20 _token, uint256 _rewardPerBlock) external onlyOwner {
    require(address(_token) != address(0), "Must be a real token");
    require(address(_token) != address(this), "Must be a real token");
    (bool foundToken, uint256 tokenIndex) = findElementPosition(_token, rewardTokens);
    require(!foundToken, "Token exists");
    rewardTokens.push(_token);
    uint256 decimalsRewardToken = uint256(_token.decimals());
    require(decimalsRewardToken < 30, "Must be inferior to 30");
    PRECISION_FACTOR[_token] = uint256(10**(uint256(30).sub(decimalsRewardToken)));
    rewardPerBlock[_token] = _rewardPerBlock;
    accTokenPerShare[_token] = 0;
    emit NewRewardToken(_token, _rewardPerBlock, PRECISION_FACTOR[_token]);
}

function updateRewardPerBlock(uint256 _rewardPerBlock, ERC20 _token) external onlyOwner {
    require(block.number < startBlock, "Pool has started");
    (bool foundToken, uint256 tokenIndex) = findElementPosition(_token, rewardTokens);
    require(foundToken, "Cannot find token");
    rewardPerBlock[_token] = _rewardPerBlock;
    emit NewRewardPerBlock(_rewardPerBlock, _token);
}
```

Note the other routine, i.e., updateStartAndEndBlocks(), can also beneﬁt from this improvement.

## Recommendation
Timely invoke _updatePool() when reward-related conﬁguration has been updated in above-mentioned routines.
