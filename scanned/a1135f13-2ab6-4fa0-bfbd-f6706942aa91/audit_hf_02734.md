# [M] Cross SeaDrop reentrancy

## Summary
Severity: Medium
Contest weight: 0.1732
Dataset id: 14919
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract that implements IERC721SeaDrop can work with multiple Seadrop implementations, for example, a Seadrop that accepts ETH as payment as well as another Seadrop contract that accepts USDC as payment at the same time. This introduces the risk of cross contract re-entrancy that can be used to circumvent the maxMintsPerWallet check. Here's an example of the attack:
1. Consider an ERC721 token that that has two allowed SeaDrop, one that accepts ETH as payment and the other that accepts USDC as payment, both with public mints and restrictedFeeRecipients set to false.
2. Let maxMintPerWallet be 1 for both these cases.
3. A malicious fee receiver can now do the following:
• Call mintPublic for the Seadrop with ETH fees, which does the _checkMintQuantity check and transfers the fees in ETH to the receiver.
• The receiver now calls mintPublic for Seadrop with USDC fees, which does the _checkMintQuantity check that still passes.
• The mint succeeds in the Seadrop-USDC case.
• The mint succeeds in the Seadrop-ETH case.
• The minter has 2 NFTs even though it's capped at 1.
Even if a re-entrancy lock is added in the SeaDrop, the same issue persists as it only enters each Seadrop contract once.

## Recommendation
Consider adding a reentrancy lock in the ERC-721 contract. Also see the related issue Reentrancy of fee payment can be used to circumvent max mints per wallet check about reentrancy.
