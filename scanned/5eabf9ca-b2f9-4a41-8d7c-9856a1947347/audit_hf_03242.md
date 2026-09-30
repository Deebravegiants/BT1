# [M] GLOBAL-4 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.1379
Dataset id: 17861
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The exchange keeper and other permissioned addresses have the power to do nearly anything: Execute any order or liquidation at any arbitrary price Defer execution of any arbitrary deposit, withdrawal, order, or liquidation Select the order of execution for all incoming deposits, withdrawals, and orders Power to shut off any feature – including withdrawals and closing positions Change out the protocol-wide variables used in the dataStore There are many assumptions made on the form of the price input from the keeper. Adding validation for the expected format and range of acceptable inputs would reduce the risk of high-cost mistakes, and assist in limiting the scope of the internal exploits available to the keeper. The keeper must diligently execute orders, for example stop loss orders must be executed with the correct range of prices while staying within the MAX_ORACLE_PRICE_AGE limit.

## Recommendation
Treat the keeper’s private key(s) with the utmost level of security and introduce as many safeguard checks as possible to limit the scope of the keepers potential attack vectors.
