# [H] Lack rewardStored Reset in SaleLabOverﬂowFarm::harvestOverﬂowReward()

## Summary
Severity: High
Contest weight: 0.6176
Dataset id: 12396
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LineaBank protocol, the SaleLabOverflowFarm contract performs as an IDO contract which collects users deposit of the raising tokens and offers users with the offering tokens. Meanwhile, the user can earn the reward tokens from the IDO. While reviewing the harvest logic of the reward tokens, we notice an issue that a user may repeat the harvest operations to drain all the reward tokens in the contract.
To elaborate, we show below the code snippet of the SaleLabOverflowFarm::harvestOverflowReward() function. As the name indicates, it is used by the user to harvest the rewards. It basically calculates the new pending rewards (line 168), adds the stored rewards (line 169), i.e., rewardStored[msg.sender], and then transfers all the pending rewards to the user (line 171).
However, it comes to our attention that it doesn't reset the rewardStored[msg.sender] after the harvest. As a result, the user can repeatedly harvest to drain all the rewards in the contract. Our analysis shows that it should reset the rewardStored[msg.sender] after the harvest.
```solidity
function harvestOverflowReward()
    external
    override
    nonReentrant
{
    require(block.timestamp > harvestTime(), "not harvest time");
    UserInfo storage user = userInfo[msg.sender];
    _updatePool();
    uint256 pending = 0;
    if (user.amount > 0) {
        pending = user.amount.mul(accTokenPerShare).div(1e18).sub(user.rewardDebt);
        pending = pending.add(rewardStored[msg.sender]);
        if (pending > 0) {
            address(rewardToken).safeTransfer(msg.sender, pending);
            user.rewardDebt = user.amount.mul(accTokenPerShare).div(1e18);
```
Public

## Recommendation
Revisit the SaleLabOverflowFarm::harvestOverflowReward() function to reset the rewardStored[msg.sender] after the harvest.
