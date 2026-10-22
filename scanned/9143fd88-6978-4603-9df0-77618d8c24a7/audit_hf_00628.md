# [M] M-05 | Lack Of A Grace Period For Configuration Changes

## Summary
Severity: Medium
Contest weight: 0.0952
Dataset id: 2129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract’s use of setConfig calls to modify critical parameters, such as MCP_ADL_MAX_PNL_RATE and other parameters, can impose immediate and drastic changes to the trading environment without providing users any time to adjust their positions. Sudden alterations to margin requirements, liquidation thresholds or other essential settings can leave traders caught off guard and result in unexpected position losses and forced liquidations.

## Recommendation
Introduce a delayed activation mechanism for all configuration changes. When a setConfig call modifies a critical parameter, the new value should enter a pending state for a predefined buffer period, for example 24 hours, before it becomes effective. During this transitional time frame, traders can receive alerts or monitor upcoming changes, ensuring they have sufficient time to rebalance their portfolios, add collateral or close their positions.
