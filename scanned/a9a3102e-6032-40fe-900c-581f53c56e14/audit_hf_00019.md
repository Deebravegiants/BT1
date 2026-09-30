# [M] BIN-1 | Option May Have Time Value But Zero Premium

## Summary
Severity: Medium
Contest weight: 0.0999
Dataset id: 95
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An option’s premium is calculated to be Premium = Time Value + Intrinsic Value. Consequently, even if an option is out-the-money (no intrinsic value), if there is still time until expiration the premium should be non-zero. Due to the specific 15 periods and volatility factors used for binomial calculation, it is possible for all of the terminal payoffs to be zero and result in the option’s premium to be zero. Trader may buy a contract for 0 premium and then sell it as price moves in their favor allowing for nearly risk-free trades. Health Ratio Not Validated Correctly Put-Call Parity Equation Is Invalidated

## Recommendation
Consistently monitor volatility parameters and consider increasing how many periods are used for Binomial options pricing.
