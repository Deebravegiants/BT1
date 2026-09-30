# [H] H-04 | All Credit Interests Are Deployed As Liquidity

## Summary
Severity: High
Contest weight: 0.1337
Dataset id: 2209
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CreditFacility _sendReserves function used to keep the interest reserves amount in the CreditFacility contract so that this amount could be removed by the fee receiver which is approved for the CreditFacility. However now, because the removeAllFrom function leaves all removed tokens in the BPOOL contract, the interest amount is not collected by the protocol and will instead be deployed back into the liquidity structure.

## Recommendation
Use BPOOL.transferToken(reserve, feeRecipient, _interest); in the _sendReserves function. Additionally, remove the feeRecipient approval logic as it is no longer necessary.
