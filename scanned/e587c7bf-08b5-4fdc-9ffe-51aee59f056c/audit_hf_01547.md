# [M] Users can claim tokens in ConnextRouter by calling xReceive(...) directly

## Summary
Severity: Medium
Contest weight: 0.1093
Dataset id: 8227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ConnextRouter allows anyone to call xReceive(...) and the amount of assets the user provided is the balance of the contract. Thus, users can use this functionality to sweep any existing funds into their wallets. In fact, this should also happen when a xReceive(...) call fails at this.xBundleConnext(...), and the balance, including the existing tokens, get attributed to the user. It should not be a likely event given that there are checks to ensure that the ConnextRouter does not end up with funds after xBundle(...) calls. Still, given that the BaseRouter has a sweepTokens(...) function, this might lead to a false sense of security.

## Recommendation
Only let a permissioned address call xReceive(...) (should be the xConnect address). Additionally, instead of sending the balance in the ConnextRouter if this.xBundleConnext(actions, args, beforeSlipped) fails, send the amount.
