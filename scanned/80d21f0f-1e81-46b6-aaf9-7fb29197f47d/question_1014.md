# Q1014: Compression/encoding step in undistort_coordinates leaks or corrupts (image/fisheye.rs)

## Question
Can an unprivileged attacker exploit the compression/encoding in `undistort_coordinates` in [src/image/fisheye.rs](src/image/fisheye.rs) — non-constant-size output, side-channel-revealing lengths, or corrupt output on adversarial input — to learn or corrupt biometric content it processes?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `undistort_coordinates` (function)
- Entrypoint: Capture content shaping the compressor's input
- Attacker controls: the entropy/structure of the captured content
- Exploit idea: Check `undistort_coordinates` for bounded, validated output and whether length reveals content.
- Invariant to test: Encoded output length and success do not depend on secret content in an observable way.
- Expected Immunefi impact: Information leakage or corruption of the biometric package
- Fast validation: Statistical/round-trip test over `undistort_coordinates` asserting integrity and length-independence.
