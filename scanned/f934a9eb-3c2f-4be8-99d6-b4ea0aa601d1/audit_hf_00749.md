# [M] M-13 | Market DOS From Direct Reset Or Resolve

## Summary
Severity: Medium
Contest weight: 0.2206
Dataset id: 2306
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A market can be resolved or reset by the owner directly from the TruthMarketManager contract. One
instance where this will be used is, if a market is paused, only the owner can call the reset or resolve
market functions instead of following the general flow through either the OracleCouncil contract or
the Escalation contract.
The issue is that when called directly, the dispute or escalation processes are not fully completed as
they would be in the general flow. In the dispute case, for instance, one issue would be the
marketLastClosedDispute not being updated, meaning the isResolverPunished and
isDisputorPunished flags remain unset, defaulting to false.
Consequently, when the market either resets or finalizes, it will attempt to send funds to the
disputer’s address fetching the address from the unset marketLastClosedDispute. Since this
address is not set, it would return the zero address, leading to a revert and locking up the market.
Furthermore, the marketClosedForDisputes is also not set to true as done in the general flow,
meaning unclaimed disputes for the market will remain locked.
Similarly, in the escalation case, if called directly for either reset or resolve, the lack of updates to
marketToEscalatedDispute will leave multiple variables such as punishment outcomes empty.
This will also cause incorrect outcomes, as the punishment outcomes will all default to false and
possibly other issues.

## Proof of Concept
https://github.com/GuardianAudits/truth-markets-2/blob/3564c644d4a874d187adfbe6d748156bd0abcfdd/test/Guardian/poc_direct_resolve.t.sol#L347

## Recommendation
In the current code, a direct call to reset or resolve the market will cause multiple issues, potentially
locking up the market and user funds. Either modify the logic to ensure that if called directly, the
dispute or escalation processes are still fully completed, or avoid calling them directly entirely.
