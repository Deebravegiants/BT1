# [H] SQPR-2 | Winners Can’t Get Prize

## Summary
Severity: High
Contest weight: 0.0419
Dataset id: 16202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition that occurs when the contract attempts to distribute prize money to a large set of winners in a single transaction. The root cause is an unbounded iteration over the list of winners that can require more gas than the block gas limit permits. When the number of winners grows, the cumulative gas needed for the loop exceeds the maximum gas that can be included in a block, causing the entire payout transaction to revert. An attacker or even a legitimate user can trigger the payout function, but the transaction will fail with an out‑of‑gas error, preventing any winner from receiving their prize. The impact is that funds allocated for prizes become effectively locked in the contract, users see their expected balances remain zero, and the user interface may display that a prize was awarded while the on‑chain state shows no transfer. This condition occurs only under the circumstance that the winner set is sufficiently large; small winner sets succeed, making the problem easy to miss during normal testing. The issue was discovered during a security audit that examined the prize distribution logic and identified the potential for gas exhaustion. It is hard to notice because the contract behaves correctly for typical cases, and the failure only manifests at scale. Conceptually, the bug belongs to the class of “mass‑payout” or “unbounded loop” vulnerabilities that violate the assumption that a contract can safely push funds to an arbitrary number of recipients in one call. From a user’s perspective, a winner may attempt to claim a reward and receive a transaction failure, see no change in their balance, or receive a message that the prize could not be claimed. The recommended mitigation is to replace the push‑style payout with a pull‑over‑push withdrawal pattern, allowing each winner to individually withdraw their prize in separate transactions that stay within the gas limit, thereby preserving the accounting guarantees and preventing funds from becoming inaccessible.

## Recommendation
Utilize a pull-over-push withdrawal patten.
