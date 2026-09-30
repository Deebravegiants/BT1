# [M] Misconfigured decimal scale can skew vault accounting

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23355
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The vault’s math assumes the same decimal scale as the wrapped asset (USDC, 6 decimals) and as the globalPricePerShare fed by ops. While deployment sets vaultParams.decimals = 6 and the wrapper enforces USDC’s 6 decimals, a misconfiguration will skew conversions.
Impact: Configuring the vault with more than 6 decimals can cause incorrect accounting, and follow‑on reverts in rebalancing.

## Recommendation
Recommended Mitigation: Consider locking the vault decimals to 6, same as SherpaUSD.
