# [M] Improper stakeDate Updated In unstake()

## Summary
Severity: Medium
Contest weight: 0.4032
Dataset id: 13298
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function unstake(uint256 _amount) public whenNotPaused {
    require(_amount > 0, "Amount must be greater than Zero.");
    require(stakes[msg.sender].amount > 0, "Stake Amount must be greater than Zero.");
    require(block.timestamp >= stakes[msg.sender].stakeDate.add(2592000), "You must wait at least a month to unstake.");
    uint256 _dateDiff = block.timestamp.sub(stakes[msg.sender].stakeDate);
    uint256 _totalAmount = stakes[msg.sender].amount.add(stakes[msg.sender].amount.mul(stakePercentage).mul(_dateDiff).div(3153600000));
    require(_totalAmount >= _amount, "Amount cannot be greater than your stake.");
    uint256 _scaledAmount = _amount.mul(uint256(10)**tokenContract.decimals());
    require(tokenContract.transfer(msg.sender, _scaledAmount), "Token Transfer Contract failed.");
    stakes[msg.sender].amount = _totalAmount.sub(_amount);
    stakes[msg.sender].stakeDate = block.timestamp;
}
```

## Recommendation
The stakeDate should not be updated in the unstake() function.
