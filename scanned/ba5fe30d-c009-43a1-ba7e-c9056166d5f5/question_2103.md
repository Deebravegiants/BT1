# Q2103: Zero-copy/archived access in iris_normalized_images without validation (debug_report.rs)

## Question
Can an unprivileged attacker supply bytes that `iris_normalized_images` in [src/debug_report.rs](src/debug_report.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `iris_normalized_images` (function)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `iris_normalized_images` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `iris_normalized_images` over arbitrary bytes asserting checked access and no UB.
