# [M] M-12 | Insufficient Gas Forwarded For Refund

## Summary
Severity: Medium
Contest weight: 0.1451
Dataset id: 21893
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the refundExecutionFee function the REFUND_EXECUTION_FEE_GAS_LIMIT is forwarded to the callbackContract when calling the refundExecutionFee value. However the transaction execution is not validated to have the necessary REFUND_EXECUTION_FEE_GAS_LIMIT with the gas left for the transaction. As the REFUND_EXECUTION_FEE_GAS_LIMIT is currently configured to 200,000 gas units and the refundExecutionFee call takes place at the end of action executions it is possible that keepers would not have provided enough gas to forward the entire limit. Instead 63/64 of the remaining gas left will be forwarded to the refundExecutionFee function call in these cases. This may cause unexpected reverts for integrating systems and result in mis-accounted funds. However this instance of not validating the gas left with the validateGasLeftForCallback is not as severe as the lack of this validation for the GLV callbacks, as the refund fee is configured with a lower gas limit and handles less funds.

## Recommendation
Validate the gas left for the refundExecutionFee callback with the validateGasLeftForCallback function.
