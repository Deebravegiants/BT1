# [C] DIEM-1 | Liquidations Halted Due To DoS

## Summary
Severity: Critical
Contest weight: 0.1460
Dataset id: 82
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no limit to the amount of trades a user may open in their portfolio. Therefore it is possible for a user to open so many trades that functions that need to iterate through all of them multiple times, such as liquidation, cannot occur. The maxBatchTrading validation fails to protect against this DoS as it limits only the amount of trades that can be opened in a single openTrades function call.

## Proof of Concept
https://github.com/GuardianAudits/IVX-Suite/blob/main/test/guardian/DIEM-1.sol

## Recommendation
Implement a cap on the amount of trades that can belong to any single portfolio.
