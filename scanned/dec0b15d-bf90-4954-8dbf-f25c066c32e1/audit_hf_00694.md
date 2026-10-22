# [M] M-15 | Streaming Fee Starts Too Late

## Summary
Severity: Medium
Contest weight: 0.0433
Dataset id: 2245
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a business‑logic flaw in the streaming‑fee mechanism of the long‑term (LT) position contract. The protocol is designed to charge a 2 % per‑year fee on the notional value of an LT position, but the implementation only begins to accrue this fee when the first redemption transaction is executed. Consequently, if a user deposits an LT position and then holds it without ever redeeming, the fee never starts to accumulate, allowing the user to keep the position fee‑free for an indefinite period. The root cause is that the fee‑accrual trigger is tied to a redemption event rather than to the initial deposit or any subsequent rebalance, which is the moment when the economic exposure actually begins. An attacker or a regular user can exploit this by simply never calling the redeem function, thereby avoiding the intended streaming fee entirely. The impact is a loss of revenue for the protocol because the fee that should have been collected over time is never realized, potentially undermining the economic model and reducing funds available for protocol maintenance or token holders. This condition occurs whenever an LT position is created and the holder chooses not to redeem for a prolonged time; it does not affect users who redeem normally, as they will see the fee applied at redemption. The affected parties include the protocol itself, its token holders, and any stakeholders relying on the fee revenue stream. The issue was discovered during a security audit that examined the fee‑calculation flow and identified that the fee start timestamp was incorrectly set. It can be hard to notice because the fee appears correct after a redemption, masking the fact that earlier periods generated no fee. From a user’s perspective the UI may show a zero streaming‑fee amount and the balance remains unchanged, leading the user to believe they are not being charged. In reality the protocol is losing expected income. The recommended remediation is to initialize fee accrual at the moment of the first deposit or any rebalance operation, ensuring that the fee starts counting from the moment the position becomes active, and to adjust the accounting logic accordingly. This aligns the implementation with the intended economic model and prevents revenue leakage.

## Recommendation
Start to accrue the streaming fees in the ﬁrst deposit/rebalance instead of the ﬁrst redemption.
