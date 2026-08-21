# Q2201: Compression/encoding step in from leaks or corrupts (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `from` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `from` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `from` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `from` asserting integrity and length-independence.
