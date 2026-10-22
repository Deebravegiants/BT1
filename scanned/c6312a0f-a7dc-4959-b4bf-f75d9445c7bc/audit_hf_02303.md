# [M] Non ERC20-Compliance Of CToken

## Summary
Severity: Medium
Contest weight: 0.0190
Dataset id: 12559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a CToken contract that does not fully comply with the ERC20 token standard. The root cause is that the implementation omits or incorrectly implements several view‑only functions defined in the ERC20 specification, such as name, symbol, decimals, totalSupply, balanceOf, and allowance, or returns values that do not match the expected semantics. Because many external contracts, wallets, and DeFi protocols rely on these functions to query token metadata and accounting information, the non‑compliant behavior can be exploited by feeding malformed or missing data into dependent logic. An attacker could trigger a failure in a downstream contract that assumes a correct totalSupply value, causing the contract to revert or to miscalculate rewards, which may lead to funds being locked or lost. The impact is that token holders may see their balances appear as zero, UI components may display missing symbols or decimals, and automated systems may reject the token altogether, breaking integrations and potentially causing financial loss. The issue manifests whenever any caller invokes an ERC20 view function on the CToken, which can happen during token transfers, allowance checks, or when a front‑end queries token metadata. All users, integrators, and protocols that interact with the CToken are affected because they expect standard ERC20 behavior. The problem was discovered during a manual audit where the auditor compared the contract’s public interface against the ERC20 specification and identified missing or non‑standard functions. The bug is subtle because the contract may still allow transfers, giving the impression that it works, while the missing view functions cause silent failures in dependent code. To remediate, the CToken should be revised to implement the full ERC20 interface, ensuring that each required view function returns correct values, that events are emitted as defined, and that the contract adheres to the exact function signatures and return types prescribed by the ERC20 standard. This correction restores compatibility with wallets, DeFi protocols, and any other system that assumes ERC20 compliance, eliminating the risk of unexpected zero balances, missing token metadata, and integration failures.

## Recommendation
Revise the CToken implementation to ensure its ERC20-compliance.
