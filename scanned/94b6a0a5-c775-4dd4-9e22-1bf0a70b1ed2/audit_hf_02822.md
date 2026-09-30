# [M] Locked splits can be updated

## Summary
Severity: Medium
Contest weight: 0.1809
Dataset id: 15630
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The check if the newly provided project splits contain the currently locked splits does not check the `JBSplit` struct properties `preferClaimed` and `preferAddToBalance`.

According to the docs in `JBSplit.sol`, _“…if the split should be unchangeable until the specified time, with the exception of extending the locked period.”_ , locked sets are unchangeable.

However, locked sets with either `preferClaimed` or `preferAddToBalance` set to true can have their bool values overwritten by supplying the same split just with different bool values.

## Proof of Concept
[JBSplitsStore.sol#L213-L220](https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/JBSplitsStore.sol#L213-L220)

The check for sameness does not check the equality of the struct properties `preferClaimed` and `preferAddToBalance`.

_Please see warden’s[original report](https://github.com/code-423n4/2022-07-juicebox-findings/issues/278) for full PoC and Mitigation details._

## Recommendation
Add two additional sameness checks for `preferClaimed` and `preferAddToBalance`:

**mejango (Juicebox) resolved:**

PR with fix: [PR #1](https://github.com/jbx-protocol/juice-contracts-v3/pull/1)

**berndartmueller (warden) reviewed mitigation:**

Two additional sameness checks for the split properties `preferClaimed` and `preferAddToBalance` have been added.
