# [M] M-11 | Check If Asset Is Known In Deposit Flow

## Summary
Severity: Medium
Contest weight: 0.0865
Dataset id: 2563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PositionManager contract contains two mappings, isKnownAddress and isKnownFunc, which define the universe of the protocol. isKnownAddress specifies recognized addresses that a Position can interact with. The transfer function verifies whether the token is known as expected. However, the deposit function lacks this validation. Borrowers can deposit any asset to their position as collateral, causing these tokens to become locked since users are unable to transfer them afterwards. An analogous issue is present in the addToken function.

## Recommendation
Ensure that the address is verified in these functions.
