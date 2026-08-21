# Q1010: Zero-copy/archived access in Command without validation (process.rs)

## Question
Can an unprivileged attacker supply bytes that `Command` in [src/process.rs](src/process.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/process.rs](src/process.rs) -> `Command` (type)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `Command` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `Command` over arbitrary bytes asserting checked access and no UB.
