# [H] GVH-1 | DOS Rebalance Through Simple Transfer

## Summary
Severity: High
Contest weight: 0.2090
Dataset id: 20524
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A Denial of Service (DoS) attack can occur on rebalances by forcing the Umami-calculated estimateExecutionFee to be less than GMX’s minExecutionFee. As only one token is being deposited on a rebalance, Umami calculates the estimateExecutionFee and enters an if statement, returning the smaller value compared to if it were to deposit two tokens.

The issue arises when an attacker forcibly sends 1 wei of the opposite token to GMX. The other gas limit value is then used, which is greater than what Umami used to calculate estimateExecutionFee. This leads to a revert in the validateExecutionFee function. With this attack, it becomes impossible to perform a rebalance, rendering the core feature of the protocol unusable.

## Recommendation
Send excess WETH for the execution fee, as any excess would be refunded anyway. This mitigates the risk of the DoS attack and ensures the rebalance functionality remains functional.
