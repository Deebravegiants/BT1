# [M] IERC20(token).approve revert if the underly-

## Summary
Severity: Medium
Contest weight: 0.5551
Dataset id: 20188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
IERC20(token).approve revert if the underlying ERC20 token approve does not return boolean. When transferring the token, the protocol use safeTransfer and safeTransferFrom but when approving the payout token, the safeApprove is not used. For non-standard token such as USDT, calling approve will revert because the solmate ERC20 enforces the underlying token return a boolean.
```solidity
https://github.com/transmissions11/solmate/blob/bfc9c25865a274a7827fea5abf6
e4fb64fc64e6c/src/tokens/ERC20.sol#L68
function approve(address spender, uint256 amount) public virtual returns (bool) {
    allowance[msg.sender][spender] = amount;
    emit Approval(msg.sender, spender, amount);
    return true;
}
```
While the token such as USDT does not return boolean.
```solidity
https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#
code#L126
```
USDT or other ERC20 token that does not return boolean for approve is not supported as the payout token.

## Recommendation
Use safeApprove instead of approve.
