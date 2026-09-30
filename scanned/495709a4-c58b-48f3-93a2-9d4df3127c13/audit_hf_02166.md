# [M] Revisited Staking Logic in StakingInterface::stake()

## Summary
Severity: Medium
Contest weight: 0.4436
Dataset id: 12094
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Staking support allows users earn passive income as the FEG ecosystem-generated fees feed the staking rewards. While examining the current staking logic, we notice the implementation may need to be revisited. In particular, we show below the related implementation of the StakingInterface::stake() routine. It has a rather straightforward logic in transfering the staking token from the user into itself, which then immediately forwards the staking token to the stakeLogic contract. It comes to our attention that the staking token is a reflection one which might have a transfer fee. As a result, the forwarding amount may not be the same as the initial staking amount. In other words, we need to properly use the actual received amount for the forwarding, instead of the initial amount. Note the StakingLogic contract also has a stake() routine, which shares the same issue. Moreover, we notice the staking token is eventually saved in the StakingInterface contract. As a result, the staking funds via the following StakingInterface::stake() routine will in essence tranfer the reflection token back and forth between StakingInterface and StakingLogic, which should be avoided to save unnecessary transfer fee.
```solidity
function stake(uint256 amount) public nonReentrant returns(uint256 poolAmountOut) {
    SafeTransfer.safeTransferFrom(IERC20(SD), msg.sender, address(this), amount);
    SafeTransfer.safeTransfer(IERC20(SD), stakeLogic, amount);
    poolAmountOut = StakeLogics(stakeLogic).stake(msg.sender, amount);
    emit STAKED(msg.sender, amount);
    emit Transfer(msg.sender, address(this), poolAmountOut);
    return poolAmountOut;
}
```

## Recommendation
Revisit the above staking logic to ensure the staking amount is properly accounted for and no extra transfer fee is charged.
