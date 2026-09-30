# [M] Not using SafeTransferLib

## Summary
Severity: Medium
Contest weight: 0.4239
Dataset id: 10057
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Most of the token transfer operations within the Pool already utilize
SafeTransferLib. However, several operations, including those in
removeLiquidity, rescue, and skim, still use the unsafe transfer method.
Consider adjusting these transfer operations to also utilize SafeTransferLib.
The rescue function is designed to withdraw all tokens mistakenly sent to the
contract, excluding the supported tokens listed in the tokens array. However,
the function fails for non-standard ERC20 tokens that do not return a boolean
value on transfer (e.g., USDT). This causes the contract to revert, preventing
the rescue of those tokens.
function rescue(address token_, address receiver_) external onlyOwner {
    uint256 _numTokens = numTokens;
    for (uint256 t = 0; t < MAX_NUM_TOKENS; t++) {
        if (t == _numTokens) break;
        if (!(token_ != tokens[t])) revert Pool__CannotRescuePoolToken();
        uint256 _amount = ERC20(token_).balanceOf(address(this));
        ERC20(token_).transfer(receiver_, _amount);
    }
}
In addition, the current implementation of Pool.removeLiquidity() does not
support tokens that do not return a boolean on successful transfers. The issue
lies in the following code:
if (!(ERC20(tokens[t]).transfer
(receiver_, amount))) revert Pool__TransferFailed();
```

## Recommendation
Consider using SafeTransferLib.safeTransfer() to handle such tokens.
