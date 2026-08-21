# Q1855: Type/enum default in init maps to a benign verdict (rgb-net/lib.rs)

## Question
Can an unprivileged attacker reach a path where `init` in [rgb-net/src/lib.rs](rgb-net/src/lib.rs) constructs its result via `Default`/`unwrap_or_default`, yielding zeroed scores or a benign enum variant that downstream logic reads as 'no problem found'?

## Target
- File/function: [rgb-net/src/lib.rs](rgb-net/src/lib.rs) -> `init` (function)
- Entrypoint: Any path where the real value is unavailable
- Attacker controls: conditions preventing the real value from being produced
- Exploit idea: Check the `Default` semantics of the type built by `init` against how consumers interpret it.
- Invariant to test: No security-relevant type has a `Default` that reads as a passing verdict.
- Expected Immunefi impact: Fraud verdict defaulted to benign for a capture that was never evaluated
- Fast validation: Unit-test asserting the default value of `init`'s result is rejected by every consumer.
