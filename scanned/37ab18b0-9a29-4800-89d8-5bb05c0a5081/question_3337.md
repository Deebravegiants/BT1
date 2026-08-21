# Q3337: Compression/encoding step in format_newstyle_daemon leaks or corrupts (logger.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `format_newstyle_daemon` in [src/logger.rs](src/logger.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `format_newstyle_daemon` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `format_newstyle_daemon` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `format_newstyle_daemon` asserting integrity and length-independence.
