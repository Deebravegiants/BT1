# Q2176: Compression/encoding step in available_space leaks or corrupts (ssd.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `available_space` in [src/ssd.rs](src/ssd.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `available_space` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `available_space` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `available_space` asserting integrity and length-independence.
