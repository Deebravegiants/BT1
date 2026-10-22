# [M] Wrong price calculation in DnGmxJuniorVault-

## Summary
Severity: Medium
Contest weight: 0.0797
Dataset id: 17761
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in DnGmxJuniorVaultManager.sol at line:647: usdcPrice should be on denominator and MAX_PRECISION on numerator (cf pricing in Vault: uint256 redemptionAmount = _usdgAmount.mul(PRICE_PRECISION).div(price);)
In the case usdcPrice is higher than 1$ (which already happened in reasonable market circumstances). Min amount expected will be higher than swap result under 0% slippage conditions. The call will revert, which will delay rebalances until usdcPrice comes back to 1$, and causing potential loss to the protocol.

## Recommendation
Recommendation in summary
