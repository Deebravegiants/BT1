# [M] `withdrawFromWETH` always reverts

## Summary
Severity: Medium
Contest weight: 0.0934
Dataset id: 951
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `TridentHelper.withdrawFromWETH` (used in `TridentRouter.unwrapWETH`) function performs a low-level call to `WETH.withdraw(amount)`.

It then checks if the return `data` length is more or equal to `32` bytes, however `WETH.withdraw` returns `void` and has a return value of `0`. Thus, the function always reverts even if `success == true`.
    
    function withdrawFromWETH(uint256 amount) internal {
        // @audit WETH.withdraw returns nothing, data.length always zero. this always reverts
        require(success && data.length >= 32, "WITHDRAW_FROM_WETH_FAILED");
    }

## Recommendation
Remove the `data.length >= 32` from the require and only check if `success` is true.
