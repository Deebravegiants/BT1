# [M] M-5 The redeemObligation will always be reverted

## Summary
Severity: Medium
Contest weight: 0.0409
Dataset id: 7555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a redemption function that is intended to let users withdraw their obligations while the protocol is in the Outcome.ONGOING state, but the function internally calls a manager routine that unconditionally reverts when the outcome is still ongoing. The root cause is a mismatch between the expected contract state and the actual state check performed in the manager code, resulting in a logical dead‑end: the redeemObligation entry point is reachable, yet any call triggers a revert at Manager.sol line 204. An attacker or even a regular user can exploit this by simply invoking redeemObligation, causing the transaction to fail and preventing the withdrawal of any locked funds. The impact is that users who expect to receive a refund or to close their position see their transaction revert, their balances remain unchanged, and the protocol’s liquidity can become permanently locked for those obligations. This condition occurs whenever the protocol reports an ongoing outcome, which is the normal state during the resolution phase, making the bug appear only in that specific window. All participants holding obligations—individual traders, liquidity providers, or any role that relies on the ability to redeem—are affected because the contract silently refuses to process the request. The issue was discovered during a systematic security audit that examined state transitions and function pre‑conditions, and it can be hard to notice because the function signature suggests it is usable, yet the internal revert is not obvious without tracing the manager call. To remediate, the contract should either adjust the manager’s state check to allow calls during Outcome.ONGOING, or replace the call with an alternative withdrawal routine that is compatible with the ongoing state, thereby restoring the intended refund path. In essence, this is a state‑validation bug that breaks the accounting logic of the protocol, leading to missing refunds and funds that appear to disappear from the user’s perspective.

## Recommendation
It is recommended to either modify Battle.withdrawObligation or use an alternative function instead in order to enable the withdrawal of obligations during the Outcome.ONGOING state. 2.4 Low
