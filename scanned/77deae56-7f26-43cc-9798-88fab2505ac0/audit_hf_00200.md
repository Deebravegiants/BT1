# [M] `exitTempusAMM` can be made to fail

## Summary
Severity: Medium
Contest weight: 0.1163
Dataset id: 1058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There’s a griefing attack where an attacker can make any user transaction for `TempusController.exitTempusAMM` fail. In `_exitTempusAMM`, the user exits their LP position and claims back yield and principal shares. The LP amounts to redeem are determined by the function parameter `lpTokensAmount`. A final `assert(tempusAMM.balanceOf(address(this)) == 0)` statement checks that the LP token amount of the contract is zero after the exit. This is only true if no other LP shares were already in the contract.

However, an attacker can frontrun this call and send the smallest unit of LP shares to the contract which then makes the original deposit-and-fix transaction fail.

## Recommendation
Remove the `assert` check.

Great finding. This can block people exiting AMM via `TempusController`.

[mijovic (Tempus) patched](https://github.com/code-423n4/2021-10-tempus-findings/issues/21#issuecomment-948350606):

Fixed in <https://github.com/tempus-finance/tempus-protocol/pull/369>
