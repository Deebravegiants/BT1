# [M] GLOBAL-1 | Unlimited Centralized Controls

## Summary
Severity: Medium
Contest weight: 0.0441
Dataset id: 94
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a set of unchecked configuration parameters that can be modified by privileged callers without any bounds checking. The contract exposes functions that allow the central authority to adjust critical economic variables such as the collateral factor, the fee taken from profits, the delta cutoff for position adjustments, the withdrawal fee, the processing limit, and the interest‑rate parameters. Because there is no validation of the supplied values, an attacker who gains access to the privileged role (or a malicious insider) can set these variables to extreme or nonsensical numbers. For example, setting the collateral factor to zero would render all user positions instantly under‑collateralized, triggering liquidations and causing users to lose their deposited assets. Similarly, inflating the withdrawal fee to 100 % would cause every withdrawal request to return no funds, effectively freezing user balances. An excessively high interest‑rate parameter could generate uncontrolled accruals, breaking the protocol’s accounting logic and leading to a mismatch between on‑chain balances and expected values. The impact manifests as loss of user funds, incorrect accounting, and a breach of the economic guarantees promised by the protocol. This flaw appears whenever a privileged account invokes the setter functions; the condition is not tied to any specific transaction pattern, making it difficult to detect during normal operation because the transactions succeed and emit no error. The issue was discovered during a systematic audit of the codebase, where the auditor noted the absence of any require statements or clamping logic around these setters. The problem is subtle because the functions themselves look benign and the parameters are expected to be mutable for governance, yet the lack of limits creates a hidden backdoor for arbitrary economic manipulation. To remediate the issue, each mutable parameter should be constrained by explicit lower and upper bounds that reflect the intended economic model, and any attempt to set values outside these ranges should cause the transaction to revert. By introducing sensible caps and rigorous input validation, the protocol can maintain its financial invariants and prevent a privileged actor from arbitrarily disabling withdrawals, draining funds, or breaking the liquidation logic.

## Recommendation
Implement limits on the range of valid values for each variable.
