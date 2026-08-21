# Q3971: Raw biometric tensors leaked by FraudChecks (plans/fraud_check.rs)

## Question
Can an unprivileged attacker cause `FraudChecks` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `FraudChecks` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `FraudChecks`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `FraudChecks` error paths asserting no biometric bytes appear in output.
