# [M] Excess ETH from deposits

## Summary
Severity: Medium
Contest weight: 0.1397
Dataset id: 11215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user can deposit WETH into the farm by calling deposit in Router.sol with msg.value > 0 and token = WETH; the ether provided with the call is wrapped to WETH. The amount that is wrapped and deposited in the farm is controlled by the user input amount.
However, there is no validation that the ether provided by the user is actually equal to the amount argument that is used to control the deposit. As a result, it is possible for a user to provide more ether than amount, yet only amount of WETH will be deposited into the farm.
The excess ETH can be stolen by the next caller by calling deposit with amount = [excess ETH]. The caller uses the excess ETH provided by the previous caller and deposits it into the farm under their address.
Similarly, a user can call this method with msg.value > 0 when intending to deposit a different token and their provided ETH will be happily accepted and can be stolen by the next user.

## Recommendation
If the token argument to the Router.sol:deposit function is WETH, then validate that amount == msg.value. Otherwise, enforce that msg.value == 0.
