# [H] Adversary can stake LP directly for the vault

## Summary
Severity: High
Contest weight: 0.7813
Dataset id: 20440
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AuraRewardPool allows users to stake directly for other users. In this case the malicious user could stake LP directly for their vault then call withdraw on their vault. This would cause the LP tracking to break on BLVaultManagerLido. The result is that some users would now be permanently trapped because their vault would revert when trying to withdraw.

```solidity
function stakeFor(address _for, uint256 _amount)
    public
    returns(bool)
{
    _processStake(_amount, _for);
    //take away from sender
    stakingToken.safeTransferFrom(msg.sender, address(this), _amount);
    emit Staked(_for, _amount);
    return true;
}
```

AuraRewardPool allows users to stake directly for another address with them receiving the staked tokens.

```solidity
auraRewardPool().withdrawAndUnwrap(lpAmount_, claim_);
// Exit Balancer pool
_exitBalancerPool(lpAmount_, minTokenAmounts_);
```

Once the LP has been staked the adversary can immediately withdraw it from their vault. This calls decreaseTotalLP on BLVaultManagerLido which now permanently breaks the LP account.

```solidity
function decreaseTotalLp(
    uint256 amount_
) external override onlyWhileActive onlyVault {
    if (amount_ > totalLp) revert BLManagerLido_InvalidLpAmount();
    totalLp -= amount_;
}
```

If the amount_ is ever greater than totalLP it will cause decreaseTotalLP to revert. By withdrawing LP that was never deposited to a vault, it permanently breaks other users from being able to withdraw.

Example: User A deposits wstETH to their vault which yields 50 LP. User B creates a vault then stake 50 LP and withdraws it from his vault. The manager now thinks there is 0 LP in vaults. When User A tries to withdraw their LP it will revert when it calls manager.decreaseTotalLp. User A is now permanently trapped in the vault. LP accounting is broken and users are permanently trapped.

## Recommendation
Individual vaults should track how much they have deposited and shouldn't be allowed to withdraw more than deposited.
