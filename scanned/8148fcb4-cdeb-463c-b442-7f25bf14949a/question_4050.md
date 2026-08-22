# Q4050: checked_add: authority bypass

## Question
In `programs/system/src/system_instruction.rs`, can an unprivileged attacker who can submit a transaction / CPI invoking the affected program path an unprivileged attacker reach `checked_add` (near line 274) and mutate, close, reassign, or debit an account whose authority never signed, breaking the invariant that no account may be mutated, reassigned, closed, or debited without its authority signing, corrupting the effective signer/writable/owner authorization used for the account?

## Target
- File/function: `programs/system/src/system_instruction.rs` :: `checked_add` (around line 274)
- Entrypoint: CPI / built-in program invocation and instruction serialization — attacker can submit a transaction / CPI invoking the affected program path
- Attacker controls: instruction data, account infos, CPI arguments, compute budget, and program ids
- Exploit idea: Can an unprivileged attacker reach `checked_add` (near line 274) and mutate, close, reassign, or debit an account whose authority never signed, so that the effective signer/writable/owner authorization used for the account is set to an attacker-chosen or inconsistent value.
- Invariant to test: no account may be mutated, reassigned, closed, or debited without its authority signing
- Expected Immunefi impact: Critical. Missing or forgeable signer, writable, ownership, or authority checks in runtime, built-in programs, or CPI let an unprivileged caller mutate, close, reassign, or drain an account whose authority never approved it.
- Fast validation: add a focused Rust unit/fuzz test on `checked_add` in `programs/system/src/system_instruction.rs` asserting the call rejects a missing/forged signer.
