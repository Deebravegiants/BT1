# Q0931: Compression/encoding step in iris_normalized_images leaks or corrupts (debug_report.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `iris_normalized_images` in [src/debug_report.rs](src/debug_report.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `iris_normalized_images` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `iris_normalized_images` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `iris_normalized_images` asserting integrity and length-independence.
