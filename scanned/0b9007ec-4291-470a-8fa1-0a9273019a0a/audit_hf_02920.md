# [M] SQDR-2 | Can’t Update Betting Fee

## Summary
Severity: Medium
Contest weight: 0.0240
Dataset id: 16245
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic error in the administrative function intended to modify the betting fee. The function, named updateBettingFees, receives a new fee value but assigns it to the variable that stores the maximum number of players instead of the variable that stores the betting fee. As a result, any attempt by the contract owner or authorized role to change the fee silently fails; the fee value stored in the contract remains the original amount. This bug originates from a simple copy‑paste or naming mistake, where the wrong state variable is written to. Exploitation does not require malicious code; an attacker can simply invoke the function (or rely on the owner’s call) and observe that the fee does not change, leading to a mismatch between the expected fee and the actual fee used in bet calculations. The impact is that the protocol cannot adjust its economic parameters, potentially causing users to overpay or underpay betting fees, breaking the intended revenue model, and making future fee adjustments impossible without redeploying the contract. The condition occurs whenever the owner calls updateBettingFees with a new fee value; the contract will instead modify maxNumberofPlayers, which may be unrelated to the fee logic. Users experience the symptom that the fee displayed in the UI remains unchanged despite the admin’s action, or that bets are accepted with an unexpected fee amount. The issue was discovered during a manual audit when the reviewer compared the function body with its specification and noticed the mismatched assignment. Because the function does not revert or emit an error, the bug can be hard to notice unless the fee value is explicitly read after the call. The vulnerability belongs to the class of incorrect state variable updates or miswired assignments, a common logical flaw that bypasses intended governance changes. To remediate, the function should assign the incoming parameter to the bettingFee storage variable (e.g., bettingFee = _newBettingFee) and optionally emit an event confirming the update. This correction restores the ability for the protocol to modify its fee and aligns on‑chain state with off‑chain expectations.

## Recommendation
Change the function body to bettingFee = _newBettingFee.
