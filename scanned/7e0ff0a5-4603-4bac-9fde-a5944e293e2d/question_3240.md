# Q3240: Compression/encoding step in get_signup_paths leaks or corrupts (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `get_signup_paths` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `get_signup_paths` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `get_signup_paths` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `get_signup_paths` asserting integrity and length-independence.
