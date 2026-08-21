# Q1007: Zero-copy/archived access in Stats without validation (ssd.rs)

## Question
Can an unprivileged attacker supply bytes that `Stats` in [src/ssd.rs](src/ssd.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `Stats` (type)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `Stats` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `Stats` over arbitrary bytes asserting checked access and no UB.
