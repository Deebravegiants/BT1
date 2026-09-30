# [M] Non ERC20-Compliance Of VToken

## Summary
Severity: Medium
Contest weight: 0.2341
Dataset id: 11877
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each asset supported by the Demeter protocol is integrated through a so-called vToken contract, which is an ERC20 compliant representation of balances supplied to the protocol. By minting vTokens, users can earn interest through the vToken's exchange rate, which increases in value relative to the underlying asset, and further gain the ability to use vTokens as collateral. In the following, we examine the ERC20 compliance of these vTokens. The ERC20 specification defines a list of API functions (and relevant events) that each token contract is expected to implement (and emit). The failure to meet these requirements means the token contract cannot be considered to be ERC20-compliant. Naturally, as part of our audit, we examine the list of API functions defined by the ERC20 specification and validate whether there exist any inconsistency or incompatibility in the implementation or the inherent business logic of the audited contract(s). Our analysis shows that there are several ERC20 inconsistency or incompatibility issues found in the vToken contract. Speciﬁcally, the current transfer() function simply returns the related error code if the sender does not have suﬃcient balance to spend. A similar issue is also present in the transferFrom() function that does not revert when the sender does not have the suﬃcient balance or the message sender does not have the enough allowance. In the surrounding two tables, we outline the respective list of basic view-only functions (Table 3.1) and key state-changing functions (Table 3.2) according to the widely-adopted ERC20 specification. In addition, we perform a further examination on certain features that are permitted by the ERC20 specification or even further extended in follow-up reﬁnements and enhancements (e.g., ERC777/ERC2222), but not required for implementation. These features are generally helpful, but

## Recommendation
Revise the VToken implementation to ensure its ERC20-compliance.
