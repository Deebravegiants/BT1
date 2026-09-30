# [H] H-04 | Wrong Cross-chain Manager Usage

## Summary
Severity: High
Contest weight: 0.1241
Dataset id: 2215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LedgerImplC holds the logic for Solana withdrawals and withdraw2Contract withdrawals. It correctly uses crossChainManagerV2Address inside executeWithdrawSolAction() to execute a Solana withdrawal. However, it uses the same crossChainManagerV2Address inside executeWithdraw2Contract() while the withdraw2Contract() function is implemented in crossChainManagerAddress. In result, withdraw2Contract() will always fail.

## Recommendation
Replace crossChainManagerV2Address with crossChainManagerAddress inside executeWithdraw2Contract().
