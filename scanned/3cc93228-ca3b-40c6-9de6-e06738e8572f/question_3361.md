# Q3361: Deserialization in check_aspect_ratio trusts length/shape fields (image/fisheye.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `check_aspect_ratio` in [src/image/fisheye.rs](src/image/fisheye.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `check_aspect_ratio` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `check_aspect_ratio` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `check_aspect_ratio` with mismatched shape headers asserting graceful rejection.
