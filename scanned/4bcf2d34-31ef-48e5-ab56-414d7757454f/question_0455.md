# Q0455: Type/enum default in FraudChecks maps to a benign verdict (plans/fraud_check.rs)

## Question
Can an unprivileged attacker reach a path where `FraudChecks` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) constructs its result via `Default`/`unwrap_or_default`, yielding zeroed scores or a benign enum variant that downstream logic reads as 'no problem found'?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `FraudChecks` (type)
- Entrypoint: Any path where the real value is unavailable
- Attacker controls: conditions preventing the real value from being produced
- Exploit idea: Check the `Default` semantics of the type built by `FraudChecks` against how consumers interpret it.
- Invariant to test: No security-relevant type has a `Default` that reads as a passing verdict.
- Expected Immunefi impact: Fraud verdict defaulted to benign for a capture that was never evaluated
- Fast validation: Unit-test asserting the default value of `FraudChecks`'s result is rejected by every consumer.
