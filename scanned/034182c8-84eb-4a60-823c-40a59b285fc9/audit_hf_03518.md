# [M] OCL-1 | Current Ref Price Compared With Earlier Price

## Summary
Severity: Medium
Contest weight: 0.0863
Dataset id: 19228
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A keeper may have to use prices from several blocks ago to execute an order, regardless of if realtime feeds or the default oracle system is being used. In such a case, the validateRefPrice would be comparing the latest Chainlink aggregator oracle price against an earlier price. Depending on how large the MAX_ORACLE_REF_PRICE_DEVIATION_FACTOR is and how volatile the asset, the execution with these earlier block numbers/prices may revert, preventing them from being used.

## Recommendation
Carefully assign the MAX_ORACLE_REF_PRICE_DEVIATION_FACTOR considering that it might be necessary in some cases to allow prices from blocks previous to when the latestAnswer in the Chainlink aggregator was updated.
