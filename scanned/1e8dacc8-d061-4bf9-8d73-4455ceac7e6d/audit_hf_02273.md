# [M] Revised Distribution of Bid Proﬁt in distribute()

## Summary
Severity: Medium
Contest weight: 0.4320
Dataset id: 12450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LuckyBid protocol, the bid proﬁt can be withdrawn and distributed to the treasury/multiFeeDistributor by the ProfitDistributor. The proﬁt is distributed to the treasury/multiFeeDistributor per a share ratio. While reviewing the distribution of the proﬁt, we notice there is a lack of distributing the desired amount of proﬁt to the multiFeeDistributor.
To elaborate, we show below the code snippet of the ProfitDistributor::distribute() routine.
As the name indicates, it is used to distribute the bid proﬁt. Firstly it calculates the proﬁt amount that belongs to the multiFeeDistributor per the shareRatio (line 60). Then it transfers the remaining amount of proﬁt, i.e., amount - shareAmount, to the treasury (line 61). However, it comes to our attention that the routine does not transfer the shareAmount of proﬁt to the multiFeeDistributor, though the shareAmount may be 0 if the shareRatio is 0. As a result, the proﬁt that belongs to the multiFeeDistributor is locked in the contract.
```solidity
function distribute(address token, uint256 amount) external {
    require(treasury != address(0), "UNSET_TREASURY");
    require(multiFeeDistributor != address(0), "UNSET_MULTI_FEE_DISTRIBUTOR");
    IERC20(token).transferFrom(msg.sender, address(this), amount);
    uint256 shareAmount = amount * shareRatio / 100;
    IERC20(token).transferFrom(address(this), treasury, amount - shareAmount);
    // TODO, distribute MultiFeeDistribution
}
```

## Recommendation
Properly transfer the shareAmount of proﬁt to the multiFeeDistributor.
