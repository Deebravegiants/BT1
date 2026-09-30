# [H] Anyone can frontrun a relayer interaction with the same arguments but a much higher/lower relayer fee

## Summary
Severity: High
Contest weight: 0.0799
Dataset id: 15205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing validation of the relayer fee parameter in the contract’s execution path, which allows any actor to submit a transaction with the same functional arguments as a legitimate user‑initiated request but with a deliberately altered relayer fee. The root cause is that the code never checks that the fee supplied in the calldata matches the fee that the user signed off‑chain, nor does it restrict the fee to be set only by the designated relayer address. Because the fee field is treated as an ordinary input, an attacker can front‑run the pending legitimate transaction, copy its payload, and replace the fee with a much lower value (stealing revenue from the relayer) or a much higher value (inflating the cost for the user). Exploitation proceeds by monitoring the mempool for a pending relayer call, broadcasting a competing transaction with identical arguments but a modified fee, and ensuring the attacker’s transaction is mined first. The impact is financial loss: the relayer may receive far less compensation than expected, while the user may be over‑charged or under‑compensated depending on the direction of the fee manipulation. This occurs whenever the contract processes a relayed operation that includes a fee argument, which is currently unchecked. All participants who rely on the fee mechanism – relayers, users, and the protocol that assumes correct accounting – are affected. The issue was discovered during a systematic audit that examined the handling of signed messages and identified that the relayer address is not enforced as msg.sender and that the fee value is not bounded or signed. Because the fee is just another integer in the calldata, the problem does not manifest as an outright revert or error, making it easy to miss during functional testing; the transaction appears successful while the economic outcome is wrong. The bug belongs to the class of “unchecked fee manipulation” or “parameter tampering” vulnerabilities, where a critical economic parameter is not cryptographically bound to the signer or the authorized actor. From a user’s perspective the UI may show a successful operation but the relayer’s balance does not increase by the expected amount, or the user’s wallet shows a higher than anticipated deduction. The expectation that the signed fee will be honored is violated, leading to a discrepancy between the promised and actual payment. To remediate, the contract should enforce that the relayer fee is either part of the signed message, that the relayer address is required to be msg.sender, and that the fee is constrained within reasonable bounds, thereby preventing arbitrary fee changes by third parties.

## Recommendation
There are several ways to tackle this issue:
1. Assert that the relayer is the msg.sender.
2. Place a cap on the relayer fee.
3. The relayer gas fee could be part of the message that the user signs.
