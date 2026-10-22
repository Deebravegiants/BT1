# [M] M-11 | Non-Discounted Collateral Used To Validate IM

## Summary
Severity: Medium
Contest weight: 0.0470
Dataset id: 21129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the margin‑validation logic of the mergeAccounts and splitAccounts functions. These functions are responsible for combining or separating user positions and must ensure that the resulting account maintains sufficient Initial Margin (IM) to cover potential losses. Instead of checking the IM against the discounted value of the collateral – which reflects the actual risk after applying the protocol’s discount factor – the code validates against the non‑discounted (full) margin value. Because the discounted value is lower, an account that appears adequately collateralised when measured with the full value may in fact be under‑collateralised after the discount is applied. This mismatch can be exploited by an attacker or an unwary user who merges or splits accounts, thereby creating a state where the protocol believes the IM requirement is satisfied while the true discounted collateral is insufficient. When market conditions move against the position, the system may trigger unexpected liquidations, loss of funds, or inability to open new trades. The issue manifests only during calls to mergeAccounts or splitAccounts, and only when the combined or separated accounts rely on discounted collateral for risk assessment. All participants that can invoke these functions – typically traders, liquidity providers, or automated bots – are affected because the protocol’s accounting assumptions are violated. The flaw was discovered during a manual audit that compared the intended risk model (discounted margin) with the actual implementation and noted the inconsistency. It can be hard to notice because the UI often displays the raw collateral amount, which looks sufficient, and the contract does not emit explicit warnings when the discounted check is bypassed. To remediate, the validation step should be rewritten to compute the discounted margin for each account and compare that value against the required IM before allowing a merge or split. This aligns the on‑chain risk checks with the protocol’s economic design and prevents accidental under‑collateralisation that could lead to fund loss or unexpected liquidation events.

## Recommendation
Validate the accounts in the mergeAccounts and splitAccounts functions against the IM based upon the discounted value of the margin.
