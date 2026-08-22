# Q4813: tpu_addr: authority bypass

## Question
In `runtime/src/bank_client.rs`, can an unprivileged attacker who can submit a transaction / CPI invoking the affected program path an unprivileged attacker reach `tpu_addr` (near line 267) and mutate, close, reassign, or debit an account whose authority never signed, breaking the invariant that no account may be mutated, reassigned, closed, or debited without its authority signing, corrupting the effective signer/writable/owner authorization used for the account?

## Target
- File/function: `runtime/src/bank_client.rs` :: `tpu_addr` (around line 267)
- Entrypoint: Transaction / instruction execution inside the bank — attacker can submit a transaction / CPI invoking the affected program path
- Attacker controls: instruction data, account set, nonce, fee payer, and program invocations
- Exploit idea: Can an unprivileged attacker reach `tpu_addr` (near line 267) and mutate, close, reassign, or debit an account whose authority never signed, so that the effective signer/writable/owner authorization used for the account is set to an attacker-chosen or inconsistent value.
- Invariant to test: no account may be mutated, reassigned, closed, or debited without its authority signing
- Expected Immunefi impact: Critical. Missing or forgeable signer, writable, ownership, or authority checks in runtime, built-in programs, or CPI let an unprivileged caller mutate, close, reassign, or drain an account whose authority never approved it.
- Fast validation: add a focused Rust unit/fuzz test on `tpu_addr` in `runtime/src/bank_client.rs` asserting the call rejects a missing/forged signer.
