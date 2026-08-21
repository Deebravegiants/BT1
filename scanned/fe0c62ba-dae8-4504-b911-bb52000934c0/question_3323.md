# Q3323: Zero-copy/archived access in ThermalCameraMetadata without validation (debug_report.rs)

## Question
Can an unprivileged attacker supply bytes that `ThermalCameraMetadata` in [src/debug_report.rs](src/debug_report.rs) accesses as an archived/zero-copy structure without full validation, so out-of-range offsets are dereferenced?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `ThermalCameraMetadata` (type)
- Entrypoint: Artifacts written earlier in the flow from attacker-influenced data
- Attacker controls: byte content of the archived buffer
- Exploit idea: Check whether `ThermalCameraMetadata` uses checked archive access rather than unchecked access.
- Invariant to test: Archived buffers are fully validated before any field access.
- Expected Immunefi impact: Memory-safety failure reachable from routine capture data
- Fast validation: Fuzz `ThermalCameraMetadata` over arbitrary bytes asserting checked access and no UB.
