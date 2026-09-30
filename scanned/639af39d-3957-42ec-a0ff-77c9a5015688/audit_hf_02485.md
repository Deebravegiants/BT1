# [M] Improper Stake Amount In stake()

## Summary
Severity: Medium
Contest weight: 0.3993
Dataset id: 13295
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function stake(uint256 _amount) public whenNotPaused {
    require(_amount > 0, "Amount must be greater than Zero.");
    require(tokenContract.balanceOf(msg.sender) >= _amount, "Amount cannot be greater than your balance.");
    uint256 _newAmount = _amount;
    if (stakes[msg.sender].amount > 0) {
        uint256 _dateDiff = block.timestamp.sub(stakes[msg.sender].stakeDate);
        _newAmount = stakes[msg.sender].amount.mul(stakePercentage).mul(_dateDiff).div(3153600000);
        _newAmount = _newAmount.add(_amount);
    }
    uint256 _scaledAmount = _newAmount.mul(uint256(10)**tokenContract.decimals());
    require(tokenContract.transferFrom(msg.sender, address(this), _scaledAmount), "Token Transfer Contract failed.");
    stakes[msg.sender].amount = _newAmount;
    stakes[msg.sender].stakeDate = block.timestamp;
}
```

## Recommendation
Transfer right amount of tokens from the user. And properly update the staked amount of the user.
