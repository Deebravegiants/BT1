# [H] Protocol insolvency risk

## Summary
Severity: High
Contest weight: 0.1499
Dataset id: 5892
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, only tokenAmounts[i] = incentiveAmount + frontendFeeAmount is pulled from the IP order creator when an IP order is created. This means that if the protocolFeeRecipient claims their fees before the order is ﬁlled, fillIPOrder will fail because the Orderbook wouldn't have enough funds to transfer to the taker.
More likely, if the order is ﬁlled before the protocolFeeRecipient claims their fees, there won't be enough funds to pay protocolFeeRecipient, causing the protocol to lose out on the protocol fees.

## Recommendation
The Orderbook should pull the entire tokenAmounts[i] = incentiveAmount + frontendFeeAmount + protocolFee from the IP order creator.
