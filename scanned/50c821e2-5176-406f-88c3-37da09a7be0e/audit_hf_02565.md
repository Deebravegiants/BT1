# [C] C-2 Mint awards can be manipulated

## Summary
Severity: Critical
Contest weight: 0.2005
Dataset id: 13783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• TroveManager.sol#L135 Mint awards can be manipulated. Next steps: 1. A hacker waits until TCR becomes 149% in TroveManager 2. The hacker takes the collateral flashloan and inside the transaction: • Open a "huge" trove to get "accountLatestMint" (mint awards TroveManager.sol#L1018). No commission due to recovery mode (https://0xsydbs-organization.gitbook.io/prisma-finance/core-protocol-operations/recovery-mode#impact-on-fees). • Open a "small" trove to increase TCR from 149% to 150% (by hacker_helper). • In the end, recovery mode is more than 150, and the hacker can close the "huge" trove without a commission. 3. The hacker has a huge "accountLatestMint" after flashloan and they can claim prisma tokens. The script has been provided.

## Recommendation
This finding shows a way to open any trove without a commission. It is not recommended to give awards for minting directly (TroveManager.sol#L1018). We recommend revising the architecture of rewards.
