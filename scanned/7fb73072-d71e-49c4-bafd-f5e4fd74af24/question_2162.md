# Q2162: Zero-copy/archived access in elapsed without validation (logger.rs)

## Question
Can an unprivileged attacker supply bytes that `elapsed` in [src/logger.rs](src/logger.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `elapsed` (function)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `elapsed` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `elapsed` over arbitrary bytes asserting checked access and no UB.
