# [M] M-5 Incorrect event

## Summary
Severity: Medium
Contest weight: 0.0129
Dataset id: 9533
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns an inaccurate event emission during the cover operation of the Lido protocol. When a user initiates a cover, the contract is supposed to burn a specific amount of stETH, removing those tokens from circulation. However, the event that is emitted at the end of the transaction still includes the burned stETH amount, as the code at StETH.sol line 461 records the full balance before the burn is applied. This mismatch between the on‑chain state (the tokens are actually destroyed) and the off‑chain observable log (the event suggests the tokens remain) creates a discrepancy in accounting. The root cause is that the event payload is constructed prior to the burn or fails to subtract the burned quantity, resulting in an event that reports a higher stETH balance than the true state. An attacker does not need to exploit the contract directly; the issue can be leveraged by any off‑chain service, analytics dashboard, or wallet that relies on events to infer token balances. Such services may display a non‑zero stETH balance after a cover, leading users to believe their funds are still available, potentially causing confusion, double‑spending attempts, or erroneous financial reporting. The impact is primarily informational: users see an unexpected non‑zero balance, UI shows “refund received” when none exists, and protocol accounting may be out of sync with the actual token supply. The condition under which this occurs is strictly the execution of the cover function where a burn is intended. All participants who depend on event data – token holders, front‑end applications, auditors, and any downstream contracts that listen to these events – are affected. The issue was identified during a manual security audit by MixBytes, who noted that the emitted event does not reflect the state change caused by the burn. It is hard to notice because the contract’s internal state correctly updates; only the emitted log is wrong, and developers often assume events are a faithful representation of state transitions. To remediate, the contract should be changed so that the event either omits the stETH amount entirely or reports the post‑burn balance, ensuring that the emitted data matches the actual token supply after the operation. This correction aligns the event with the intended business logic that burned tokens are no longer part of any user's balance, restoring accurate accounting and preventing misleading UI displays.

## Recommendation
It is necessary to exclude the stETH amount from the event.
