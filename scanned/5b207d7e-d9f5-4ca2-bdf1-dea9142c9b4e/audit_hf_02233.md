# [M] Non ERC20-Compliance Of RToken

## Summary
Severity: Medium
Contest weight: 0.1773
Dataset id: 12319
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each asset supported by the Iron Lend protocol is integrated through a so-called RToken contract, which is an ERC20 compliant representation of balances supplied to the protocol. By minting RToken's, users can earn interest through the RToken's exchange rate, which increases in value relative to the underlying asset, and further gain the ability to use RTokens as collateral. There are currently two types of RTokens: RErc20 and REther. In the following, we examine the ERC20 compliance of these RTokens. The ERC20 specification defines a list of API functions (and relevant events) that each token contract is expected to implement (and emit). The failure to meet these requirements means the token contract cannot be considered to be ERC20-compliant. Naturally, as part of our audit, we examine the list of API functions defined by the ERC20 specification and validate whether there exist any inconsistency or incompatibility in the implementation or the inherent business logic of the audited contract(s). Our analysis shows that there are several ERC20 inconsistency or incompatibility issues found in the RToken contract. Specifically, the current transfer() function simply returns the related error
Table 3.1: Basic View-Only Functions Defined in The ERC20 Specification
Item Description

## Recommendation
Revise the RToken implementation to ensure its ERC20-compliance.
