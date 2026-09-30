# [M] Incorrect Redeem Slippage Control Enforcement in Router

## Summary
Severity: Medium
Contest weight: 0.4430
Dataset id: 11791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the user interaction, the Cadabra protocol provides a Router contract that defines easy-to-use functions, i.e., invest() and redeem(). While reviewing the key redeem logic, we notice its current implementation is flawed. In the following, we show the implementation of the affected redeem() routine. It has an argument minAmounts to impose necessary minimum received amount on the receiver side after the redemption. However, it comes to our attention that the balance is measured on msg.sender (lines 92 and 100), not the given receiver.
```solidity
function redeem(
    address balancer,
    uint shares,
    IAdapter targetAdapter,
    address receiver,
    TokenAmount[] memory minAmounts,
    uint32 deadline
) external override returns (address[] memory tokens, uint[] memory amounts) {
    if (deadline < block.timestamp) {
        revert Expired(deadline);
    }
    uint256[] memory balancesBefore = new uint256[](minAmounts.length);
    for (uint i = 0; i < minAmounts.length; i++) {
        TokenAmount memory ta = minAmounts[i];
        balancesBefore[i] = IERC20(ta.token).balanceOf(msg.sender);
    }
    SafeERC20.safeTransferFrom(IERC20(balancer), msg.sender, address(this), shares);
    (tokens, amounts) = IBalancer(balancer).redeem(shares, targetAdapter, receiver);
    for (uint i = 0; i < minAmounts.length; i++) {
        TokenAmount memory ta = minAmounts[i];
        uint balanceAfter = IERC20(ta.token).balanceOf(msg.sender);
        uint diff = balanceAfter - balancesBefore[i];
        if (diff < ta.amount) {
            revert InsufficientTokenRedeemed(ta.token, diff, ta.amount);
        }
    }
}
```

## Recommendation
Revise the above redeem() routine to properly measure the balance difference so that we can enforce the minimum received amount.
