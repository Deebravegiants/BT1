# [M] Improper Return Initialization in RewardController

## Summary
Severity: Medium
Contest weight: 0.4278
Dataset id: 12373
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the reward distribution, the LayerBank protocol has a RewardController contract. It allows to lock the reward amount for a specified vestDuration. In the meantime, it also supports the early withdrawal of rewards, which may charge certain penalty if not expired. Our analysis shows the early withdrawal logic needs to be revisited. To elaborate, we show below the code snippet of the _ieeWithdrawableBalances() function. This function has a rather straightforward logic in locating the respective locked funds and compute the withdrawal amount as well as the penalty amount. We notice if the given unlockTime does not match any existing entry, the return value of index is not initialized and has the default value of 0, which may be mis-interpreted as the first entry. With that, we need to initialize the return value of index = uint256(-1) to avoid unnecessary mis-interpretation.
```solidity
function _ieeWithdrawableBalances(
    address user,
    uint256 unlockTime
) internal view returns(uint256 amount, uint256 penaltyAmount, uint256 burnAmount, uint256 index) {
    for(uint256 i = 0; i < userEarnings[user].length; i++) {
        if(userEarnings[user][i].unlockTime == unlockTime) {
            (amount, , penaltyAmount, burnAmount) = _penaltyInfo(userEarnings[user][i]);
            index = i;
            break;
        }
    }
}
```

## Recommendation
Revisit the above _ieeWithdrawableBalances() function to properly compute the locked entry for withdrawal.
