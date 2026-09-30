# [M] Improved claimable Calculation in claimable()

## Summary
Severity: Medium
Contest weight: 0.4611
Dataset id: 12750
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Pika protocol, the Vester contract is implemented to support the vesting of esPIKA token to PIKA token. The vesting is carried out by depositing certain amount of esPIKA tokens into the contract with the vesting period (set by the owner). The stakers can claim the same amount of PIKA tokens from the contract in the whole vesting period. To elaborate, we show below the code snippets of the claimable() and setVestingPeriod() routines. As the name indicate, the setVestingPeriod() is designed for the owner to update the vestingPeriod (vesting period), and the claimable() routine is designed to calculate the amount of PIKA tokens that are claimable for the given _account and _depositId. The claimable amount is calculated in proportional to the vested time in the vesting period. While examining the logic to calculate the claimable amount, it comes to our attention that, if the _depositId is created before the vestingPeriod is updated, the claimable() routine may return an unexpected amount for the given _depositId. Because the claimable amount shall be calculated per the dedicated vestingPeriod which is used to create the _depositId.
```solidity
function claimable(address _account, uint256 _depositId) public view returns (uint256) {
    UserInfo memory user = userInfo[_account][_depositId];
    if (user.vestingLastUpdate > user.vestedUntil || user.claimedAmount >= user.depositAmount)
        return 0;
    if (block.timestamp < user.vestedUntil)
        Public;
    return user.depositAmount * (block.timestamp - user.vestingLastUpdate) / vestingPeriod;

    uint256 claimableAmount = user.depositAmount * (user.vestedUntil - user.vestingLastUpdate) / vestingPeriod;
    return claimableAmount + user.claimedAmount > user.depositAmount
        ? user.depositAmount - user.claimedAmount
        : claimableAmount;
}

function setVestingPeriod(uint256 _vestingPeriod) external onlyOwner {
    vestingPeriod = _vestingPeriod;
}
```
Based on this, it is suggested to record the vestingPeriod used to create the _depositId and calculate the claimable amount per the recorded vestingPeriod.

## Recommendation
Properly revise the above claimable() routine to calculate the claimable amount of PIKA tokens with the dedicated vestingPeriod used to create the deposit.
