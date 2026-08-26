# [?] Fix ValidateCertificate proof generation to panic on preimageType overflow (#4187)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-01-14
Source: https://github.com/OffchainLabs/nitro/commit/045a16d9b3a0310ece56d163651ae036a5c65704
Type: security-commit

## Details
Fix ValidateCertificate proof generation to panic on preimageType overflow (#4187)

* Fix ValidateCertificate proof generation to panic on preimageType overflow

Update the proof generation for ValidateCertificate to use .expect()
instead of .unwrap_or(255) when converting preimageType to u8. This
ensures proof generation panics for invalid states (preimageType > 255)
rather than silently handling them.

This aligns with the Solidity one-step prover change that reverts for
this case, creating consistent behavior:
- Rust execution: ? returns Err (step can't execute)
- Rust proof gen: .expect() panics (shouldn't generate proof for invalid state)
- Solidity prover: reverts (invalid proof)

* Add changelog

---------

Co-authored-by: Joshua Colvin <jcolvin@offchainlabs.com>
