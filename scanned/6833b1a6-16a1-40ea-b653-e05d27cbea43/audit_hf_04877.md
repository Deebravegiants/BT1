# [M] Protocol is incompatible with many tokens due

## Summary
Severity: Medium
Contest weight: 0.4047
Dataset id: 22791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol is incompatible with many tokens due to unsafe transfers and approvals. The in-scope contracts all use SafeERC20 for IERC20, but don't always use the safe methods for transfers and approvals. An example in BalancerManager is shown
```solidity
IERC20 startToken = IERC20(opParams.inputToken);
require(
    startToken.allowance(msg.sender, address(this)) >= amountIn,
    "BalancerManager: insufficient allowance"
);
startToken.transferFrom(msg.sender, address(this), amountIn);
startToken.approve(address(vault), opParams.amountIn);
```
Many tokens don't conform to IERC20 and do not have return values on transfer/transferFrom and/or approve. Consequently, calling unsafe transfer and approve functions on these tokens cast to IERC20 will always revert. Protocol is unusable with many tokens that don't conform to ERC20 (there's at least one instance of an unsafe transfer or approve in every in-scope contract).

## Recommendation
Ensure that safe functions are used for ERC20 transfers and approvals (and be careful of leaving hanging approvals which would brick safeApprove).
