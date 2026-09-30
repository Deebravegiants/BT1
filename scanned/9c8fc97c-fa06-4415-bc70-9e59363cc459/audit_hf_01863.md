# [M] M-8 API3 heartbeat

## Summary
Severity: Medium
Contest weight: 0.0273
Dataset id: 10372
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the contract’s reliance on a fixed 24‑hour heartbeat interval for the API3 oracle data. The contract assumes that the oracle will provide a fresh value at least once every 24 hours and uses that value in a condition that governs critical protocol logic, such as price verification or state transitions. Because the code does not verify that the timestamp of the latest oracle update is within an acceptable freshness window, a delay longer than the expected 24‑hour period leaves the contract operating on stale data. This situation can be triggered when the API3 oracle experiences network congestion, gas price spikes, or operator downtime, causing the update transaction to be postponed beyond the heartbeat. An attacker who can influence the oracle’s update schedule—or simply wait for a natural delay—can then invoke functions that depend on the condition, causing the protocol to make decisions based on outdated information. The practical impact includes users receiving incorrect outcomes, such as trades executed at obsolete prices, refunds calculated with wrong values, or collateral checks that mistakenly pass, potentially leading to loss of funds or unfair advantage. From a user’s perspective the symptom may appear as a sudden loss of value, a zero or unexpected balance after an operation, or a missing refund that the UI shows as “0”. The issue was identified during a formal security audit by MixBytes, which noted that the heartbeat logic does not account for occasional lag. The problem is subtle because the contract does not revert or emit an explicit error when the data is stale; it simply proceeds with the last known value, making the bug hard to detect until a delay occurs. To remediate, the contract should treat the oracle value as valid only if its timestamp is within a configurable freshness margin (e.g., 30 hours) and should include fallback logic such as pausing dependent functions, reverting with a clear error, or allowing a manual update when the heartbeat is missed. This class of bug belongs to the broader category of “stale oracle data” or “insufficient freshness checks”, which violate the fundamental accounting assumption that external data reflects the current state of the world. By enforcing proper timestamp validation and handling missed heartbeats gracefully, the protocol can prevent execution based on outdated information and protect user funds.

## Recommendation
We recommend considering that the value update in the API3 oracle can take slightly more than 24 hours.
