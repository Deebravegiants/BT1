# [M] Suggested Use Of Safemath For claim()

## Summary
Severity: Medium
Contest weight: 0.4575
Dataset id: 13031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spherium protocol allows the owner to set a schedule for the user, and the schedule includes the available time and the amount of tokens for the user to withdraw from the SphrVestingStatic contract. In the following, we list below the claim() and the vestedAmount() functions. Our analysis exposes an underflow issue in both these two functions.
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

function vestedAmount() public view virtual returns (uint256) {
    VestingSchedule[] memory vestingSchedules_ = _vestingSchedules[msg.sender];
    uint256 vestedAmount_;
    for (uint256 i = 0; i < vestingSchedules_.length; i++) {
        if (vestingSchedules_[i].schedule < block.timestamp)
            vestedAmount_ += vestingSchedules_[i].amount;
    }
    vestedAmount_ -= _releaseAmount[msg.sender];
    return vestedAmount_;
}
```
The problem is when the vestedAmount_ is smaller than the _releaseAmount[msg.sender], the underflow occurs, and the vestedAmount_ will be extremely large. For the claim() function, although the safeTransfer() will revert if the contract does not have enough tokens, we still have to consider the worst condition. If the contract has enough tokens, the user can drain the funds from it. For the vestedAmount() function, it will return an extremely large vestedAmount when the user tries to check his/her own vestedAmount.

## Recommendation
Use Safemath for all the calculations in the claim() function and the vestedAmount() function.
