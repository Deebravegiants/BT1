# [M] ISU-4 | Potential For Trapped Ether

## Summary
Severity: Medium
Contest weight: 0.0365
Dataset id: 20584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a trapped Ether condition that occurs when the contract executes a branch where the internal flag wantsEth for the root address is false. In that branch the function is still marked payable, but the code does not verify that msg.value is zero nor does it return any received Ether to the caller. As a result, if a user or an attacker sends any amount of Ether with the call, the Ether is accepted by the contract and becomes permanently locked because there is no subsequent logic to withdraw or forward it. The root cause is the missing validation of the incoming value in a code path that is intended to operate without Ether, which violates the accounting assumption that the contract’s balance only changes in explicitly defined deposit functions. Exploitation is straightforward: an adversary can invoke the function with a non‑zero msg.value, causing the contract to hold the funds while the caller receives no refund and the contract provides no interface to retrieve the amount. The impact is loss of user funds and reduced confidence in the protocol, as users may see their balance become zero after a successful transaction. The condition occurs only when wantsEth[root] is false and the else branch is taken; any transaction that mistakenly includes Ether in that scenario will trigger the bug. All callers of that function are potentially affected, but the risk is greatest for users who assume that sending Ether is either prohibited or automatically returned. The issue was discovered during a manual audit that inspected payable functions and identified a branch lacking a msg.value check. Because the function does not emit an event or revert, the trapped Ether may remain unnoticed until a user inspects the contract balance and sees an unexpected reduction. To remediate, the contract should either enforce that msg.value equals zero in the non‑Ether branch or explicitly refund any received Ether to the sender before completing execution. This fixes the accounting mismatch and prevents accidental or malicious locking of funds. The bug belongs to the class of payable‑function misuse where value validation is omitted, leading to unintended balance changes and potential fund loss.

## Recommendation
Either validate that the msg.value is 0 when wantsEth[root] == false and the else case is entered, or refund this ETH to the caller.
