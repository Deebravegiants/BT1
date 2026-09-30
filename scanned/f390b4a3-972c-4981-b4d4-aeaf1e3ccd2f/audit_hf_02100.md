# [M] Potential Less Proﬁt From Permissionless unstake()

## Summary
Severity: Medium
Contest weight: 0.4314
Dataset id: 11830
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the Coin98Stake contract provides an unstake() function for users to redeem their tokens, and get their rewards. However, users are not able to redeem until the staking time exceeds the locked_time. They can also choose to continue the staking to gain higher rewards with higher reward rate. However, we find that the unstake() function is permissionless, which can be invoked by anyone. In the following, we list below the related unstake() function.
```solidity
function unstake(uint256 _tokenId) public {
    StakeInfo storage stakeInfo = StakeInfos[_tokenId];
    uint256 _profit = getStakedByTokenId(_tokenId);
    require(_profit > 0, "Not meet unstake condition");
    require(ownerOf(_tokenId) == stakeInfo.owner, "Not meet owner condition");
    uint256 _profitTotal = _profit.add(stakeInfo.amount);
    require(C98Token.balanceOf(address(this)) >= _profitTotal);
    stakeInfo.flag = false;
    C98Token.transfer(stakeInfo.owner, _profitTotal);
    totalStaked.sub(stakeInfo.amount);
    emit _unstake(_tokenId, _profitTotal, stakeInfo.time);
}
```
In the unstake() function, there is a require statement (line 1623), which checks if the owner of the NFT is original. However, there is no check for msg.sender, which means everyone can call the unstake() function to redeem for others. As a result, the user will gain less proﬁts if the redeem is brought forward.

## Recommendation
Replace the statement of require(ownerOf(_tokenId)== stakeInfo.owner, "Not meet owner condition") with require(ownerOf(_tokenId)== msg.sender, "Not meet owner condition").
