# [H] MJR-2 Incorrect change of state

## Summary
Severity: High
Contest weight: 0.0097
Dataset id: 8471
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns an improper state transition in the CreditFilter component of the Gearbox protocol. A boolean flag that determines whether a token is permitted to interact with the protocol can be switched to true directly through a function that was intended only for disabling a token. The root cause is the absence of a validation step and missing access control when setting the flag to true; the correct pathway for enabling a token is the dedicated allowToken() routine, which performs necessary checks such as token verification and risk assessment. Because the flag can be set to true without invoking allowToken(), an attacker or any caller with access to the faulty function can mark an arbitrary token as allowed. Once the flag is true, the protocol will treat the token as trusted, allowing deposits, loans, or other financial operations with that token. This can lead to the protocol accepting malicious or unsupported assets, breaking accounting assumptions, and potentially causing loss of user funds or incorrect collateral valuation. The issue manifests when the state‑changing function is called under normal operation; there is no immediate UI symptom, but later users may experience unexpected behavior such as deposits being accepted for a token that should be disabled, or refunds failing because the protocol treats the token as valid when it is not. The bug was discovered during a formal security audit performed by MixBytes, who noted that the state change to true bypasses the intended allowToken() workflow. It can be hard to notice because the boolean assignment looks innocuous and does not emit an event, so observers may not realize that a token has been inadvertently whitelisted. To remediate, the contract should restrict the state‑changing function to only allow setting the flag to false, and enforce that any transition to true must occur exclusively through allowToken(), which includes all required validation logic and emits appropriate events. This aligns the implementation with the intended security model, ensuring that only vetted tokens become usable and preserving the protocol’s financial integrity.

## Recommendation
We recommend allowing changing state only to false.
