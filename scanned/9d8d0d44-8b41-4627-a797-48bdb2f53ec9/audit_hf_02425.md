# [H] Partial Funds Can Never Be Withdrawn

## Summary
Severity: High
Contest weight: 0.6223
Dataset id: 13032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spherium protocol allows the user to withdraw a certain amount of tokens after the scheduled time. The user could have many schedules with different time and amount set by the owner.
```solidity
function claim() public returns (bool) {
    VestingSchedule[] memory vestingSchedules_ = _vestingSchedules[msg.sender];
    uint256 vestedAmount_;
    for (uint256 i = 0; i < vestingSchedules_.length; i++) {
        if (vestingSchedules_[i].schedule < block.timestamp)
            vestedAmount_ += vestingSchedules_[i].amount;
        delete vestingSchedules_[i];
    }
    vestedAmount_ -= _releaseAmount[msg.sender];
    require(vestedAmount_ > 0, "SphrVestingStatic: vested amount must be greater then 0");
    _token.safeTransfer(msg.sender, vestedAmount_);
    _releaseAmount[msg.sender] += vestedAmount_;
    return true;
}
```
To elaborate, we show above the related claim() function. An problem may occur when the user tries to call claim() multiple times to collect tokens separately. In the following, we illustrate this problem by a specific example. Assume the user has two schedules, one is 100 tokens (amount) and 5 days (time), and another one is 50 tokens and 10 days. After 5 days, the user calls claim(), and receives 100 tokens, so the _releaseAmount[msg.sender] increases to 100, then after another 5 days, when the user calls claim() again, the vestedAmount now equals to 50 this time, and the result of subtraction between the vestedAmount and the _releaseAmount[msg.sender] will be extremely large because of the underflow. If the contract does not have enough tokens, it will finally revert. Even we use the Safemath as suggested in Section 3.2, it will still revert. As a result, the user can never withdraw this part of funds.

## Recommendation
Remove the statement of vestedAmount_ -= _releaseAmount[msg.sender] (line 716) in the claim() function.
