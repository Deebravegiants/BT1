# Q5752: set_is_signer: verification bypass

## Question
In `transaction-context/src/instruction_accounts.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `set_is_signer` (near line 49) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `transaction-context/src/instruction_accounts.rs` :: `set_is_signer` (around line 49)
- Entrypoint: CPI / built-in program invocation and instruction serialization — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: instruction data, account infos, CPI arguments, compute budget, and program ids
- Exploit idea: Can `set_is_signer` (near line 49) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `set_is_signer` in `transaction-context/src/instruction_accounts.rs` asserting a forged proof/signature is rejected.
