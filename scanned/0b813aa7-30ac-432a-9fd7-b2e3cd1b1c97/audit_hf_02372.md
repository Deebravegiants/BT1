# [M] Revisited Logic in IgoOrePool::adminSafeTransfer()

## Summary
Severity: Medium
Contest weight: 0.4403
Dataset id: 12813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Project Chosen protocol has a built-in incentive mechanism that encourages participating users to stake the configured _mortgageLp for rewards. The incentive mechanism is mainly implemented in the IgoOrePool contract and our analysis shows the contract also contains a privileged function that needs to be revisited. To elaborate, we show below this privileged function adminSafeTransfer(). As the name indicates, this function facilitates the administrative transfer of the funds in the current incentive pool. However, it allows the current operator to withdraw the staked funds from protocol users. This design needs to be revisited so that the staked funds will not be jeopardized. In other words, there is a need to ensure the given _token can not be the staked token _mortgageLp with the following requirement: require(_token != _mortgageLp).
```solidity
function adminSafeTransfer(
    address _token,
    address _to,
    uint256 _amount
) public onlyOperator {
    _upgradeSafeTransfer(_token, _to, _amount);
}
function _upgradeSafeTransfer(
    address _token,
    address _to,
    uint256 _amount
) internal {
    require(_token != address(0), "Token can not be 0x0!");
    require(_amount > 0, "Transfer limit cannot be 0!");
    uint256 balance = IERC20(_token).balanceOf(address(this));
    if (_amount > balance) {
        require(
            _amount.sub(balance) < uint256(1).mul(1e18),
            "Insufficient contract balance!"
        );
        IERC20(_token).safeTransfer(_to, balance);
    } else {
        IERC20(_token).safeTransfer(_to, _amount);
    }
}
```

## Recommendation
Revise the above adminSafeTransfer() function so that the user stakes cannot be administratively transferred without their permission.
