# Q2174: Compression/encoding step in perform_async leaks or corrupts (ssd.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `perform_async` in [src/ssd.rs](src/ssd.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `perform_async` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `perform_async` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `perform_async` asserting integrity and length-independence.
