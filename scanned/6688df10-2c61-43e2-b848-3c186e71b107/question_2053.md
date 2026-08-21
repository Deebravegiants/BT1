# Q2053: Compression/encoding step in new leaks or corrupts (agents/data_uploader.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `new` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `new` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `new` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `new` asserting integrity and length-independence.
