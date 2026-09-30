# [C] PORT-1 | swapMargin Used To Game The AMM

## Summary
Severity: Critical
Contest weight: 0.2273
Dataset id: 89
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users are able to use the swapMargin function to siphon funds from their portfolio well past the point of insolvency. A user can sell options contracts to the AMM and collect the premium in their portfolio immediately. The user can then repeatedly use the swapMargin function on their portfolio and sandwich themselves to extract roughly all the value from the portfolio. The user retains their initial margin deposit as well as the premium from selling the options contracts to the AMM, without having any margin remaining in their portfolio to exercise these contracts upon expiry. A malicious user can use this attack to drain nearly all of the available funds in the IVXLP contract, after removing the balance from their portfolio they will then be insolvently liquidated.

## Recommendation
Consider removing the ability to swap margin balances as it poses an inherent risk to the system. Otherwise add validation that the portfolio is not liquidatable at the end of swapMargin function: if (IIVXDiem(diemContract).isPortfolioLiquidatable(this)) revert IVXPortfolio_PortfolioLiquidatable();
