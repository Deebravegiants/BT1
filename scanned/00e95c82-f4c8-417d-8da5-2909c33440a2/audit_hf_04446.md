# [M] No way to recover principal if an operator is removed by Chainlink

## Summary
Severity: Medium
Contest weight: 0.4102
Dataset id: 21937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** Chainlink can remove operators from the [OperatorStakingPool](https://etherscan.io/address/0xa1d76a7ca72128541e9fcacafbda3a92ef94fdc5#code). This will stop the Operator from accruing any more rewards by removing their principal. Their principal is not lost however, it is still available though by calling `OperatorStakingPool::unstakeRemovedPrincipal`.

In the `OperatorVault` there is no call like this. If an OperatorVault got removed as operator in the chainlink staking pool the pool principal would be locked.

** The funds could eventually be recovered by an upgrade to the vault but that is a long process and until then, the vault behavior would be imperfect as the removed principal is included in the vault principal:
```solidity
function getPrincipalDeposits() public view override returns (uint256) {
    return
        super.getPrincipalDeposits() +
        IOperatorStaking(address(stakeController)).getRemovedPrincipal(address(this));
}
```
Thus the vault would appear as it had the principal but it wouldn't be withdrawable.

## Recommendation
** Consider adding a call that the operator or owner can do to `unstakeRemovedPrincipal`
