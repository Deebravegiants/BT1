# [M] M-2 USDC Depeg Risk in USDX Bridge

## Summary
Severity: Medium
Contest weight: 0.0821
Dataset id: 11234
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following issue has been identified within the bridge function of the USDXBridge contract. Specifically, this involves a potential instant arbitrage risk in cases where USDC or other assets lose their peg. In such cases, the market price of USDX may depreciate because the bridge will provide an instantaneous arbitrage opportunity. This represents a risk that can impact the overall stability of the USDX token.

## Recommendation
We recommend implementing a pause function capability in the bridge functionality, allowing the operation to be temporarily halted. This could assist in risk mitigation by providing control over potential arbitrage exploitation and reducing potential market depreciation impacts.
