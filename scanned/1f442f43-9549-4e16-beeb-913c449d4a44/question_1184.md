# Q1184: Compression/encoding step in ScanError leaks or corrupts (qr_scan/mod.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `ScanError` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `ScanError` (type)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `ScanError` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `ScanError` asserting integrity and length-independence.
