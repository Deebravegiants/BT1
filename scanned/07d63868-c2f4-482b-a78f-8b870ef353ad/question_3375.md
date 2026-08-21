# Q3375: Zero-copy/archived access in as_ndarray without validation (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker supply bytes that `as_ndarray` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `as_ndarray` (function)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `as_ndarray` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `as_ndarray` over arbitrary bytes asserting checked access and no UB.
