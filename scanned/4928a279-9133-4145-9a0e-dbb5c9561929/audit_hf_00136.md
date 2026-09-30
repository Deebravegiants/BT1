# [M] `safeApprove

## Summary
Severity: Medium
Contest weight: 0.1896
Dataset id: 494
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `_depositInVault()` function for Yearn yield source uses ERC20 `safeApprove()` from OpenZeppelin’s SafeERC20 library to give maximum allowance to the Yearn Vault address if the current allowance is less than contract’s token balance.

However, the `safeApprove` function prevents changing an allowance between non-zero values to mitigate a possible front-running attack. It reverts if that is the case. Instead, the `safeIncreaseAllowance` and `safeDecreaseAllowance` functions should be used. Comment from the OZ library for this function:

“// `safeApprove` should only be called when setting an initial allowance, // or when resetting it to zero. To increase and decrease it, use // ‘safeIncreaseAllowance’ and ‘safeDecreaseAllowance’”

If the existing allowance is non-zero (say, for e.g., previously the entire balance was not deposited due to vault balance limit resulting in the allowance being reduced but not made 0), then `safeApprove()` will revert causing the user’s token deposits to fail leading to denial-of-service. The condition predicate indicates that this scenario is possible. See [similar Medium-severity finding M03](https://blog.openzeppelin.com/1inch-exchange-audit/).

Recommend using `safeIncreaseAllowance()` function instead of `safeApprove()`.

  * <https://github.com/pooltogether/pooltogether-yearnv2-yield-source/pull/new/fix/71>
  * <https://github.com/jmonteer/pooltogether-yearnv2-yield-source/pull/6>

## Recommendation
No recommendation
