# [C] DPU-5 | Swapping Collateral to PnL Token Inflates Output

## Summary
Severity: Critical
Contest weight: 0.2132
Dataset id: 17851
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After the swap from collateral token to PnL token, values.outputAmount is incremented instead of replaced with the swapOutputAmount. This leads to the addition of two different tokens which can dramatically increase the values.outputAmount depending on the PnL token’s precision. For example, if values.outputAmount represents $10,000 USDC, and then it swaps to WETH ($2000/ETH), swapOutputAmount will be 5 WETH which will get added to the $10,000 USDC. WETH, with 18 decimals of precision, will drastically inflate the user’s output. While this is unlikely to succeed due to the large difference in precision for USDC and WETH, tokens with closer precisions are highly susceptible to this bug.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1394

## Recommendation
Set values.outputAmount to 0 and values.pnlAmountForUser to swapOutputAmount.
