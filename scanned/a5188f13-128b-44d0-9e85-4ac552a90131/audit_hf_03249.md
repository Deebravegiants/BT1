# [M] ORDU-4 | Unnecessary Execution Fee

## Summary
Severity: Medium
Contest weight: 0.0400
Dataset id: 17868
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an economic misallocation where the protocol pays the executionFee to a keeper even when the order cancellation is initiated directly by the order owner. The root cause is a logic path that unconditionally transfers the executionFee to the keeper on every cancellation, without checking whether the caller is the user who placed the order or an authorized keeper. An attacker does not need to exploit a flaw; any regular user can trigger the condition simply by calling the cancel function themselves. When this happens the user’s transaction pays the normal gas cost for the cancellation and, in addition, the contract transfers the predefined executionFee to the keeper. From the user’s perspective the expected outcome is that the order is removed and only the gas used by the transaction is deducted, but in reality the user sees a larger deduction from their balance, often appearing as a “double fee” or “extra charge”. This extra cost reduces the economic efficiency of the protocol and can discourage users from managing their own orders. The issue occurs whenever a user calls the cancellation method directly, regardless of the order state, and it affects all participants who rely on self‑service order management. It was discovered during a manual audit that examined the fee handling logic and noticed that the executionFee transfer is not gated by the caller’s role. The problem can be subtle because the fee transfer looks like a normal part of the contract’s operation, making it easy to overlook that the same fee is being paid twice. To remediate, the contract should include a condition that skips the executionFee payment when the caller is the order owner, reserving the fee only for external keepers that perform automated cancellations. This change restores the intended accounting model where users only pay for the gas they consume, aligning the protocol’s incentives with its economic design and preventing unnecessary fund loss.

## Recommendation
Do not pay the executionFee to the keeper if the user is simply cancelling the order.
