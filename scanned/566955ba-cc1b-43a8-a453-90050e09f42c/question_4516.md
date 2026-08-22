# Q4516: into_address_loader_error: authority bypass

## Question
In `runtime/src/bank/address_lookup_table.rs`, can an unprivileged attacker who can submit a transaction / CPI invoking the affected program path an unprivileged attacker reach `into_address_loader_error` (near line 13) and mutate, close, reassign, or debit an account whose authority never signed, breaking the invariant that no account may be mutated, reassigned, closed, or debited without its authority signing, corrupting the effective signer/writable/owner authorization used for the account?

## Target
- File/function: `runtime/src/bank/address_lookup_table.rs` :: `into_address_loader_error` (around line 13)
- Entrypoint: Transaction / instruction execution inside the bank — attacker can submit a transaction / CPI invoking the affected program path
- Attacker controls: instruction data, account set, nonce, fee payer, and program invocations
- Exploit idea: Can an unprivileged attacker reach `into_address_loader_error` (near line 13) and mutate, close, reassign, or debit an account whose authority never signed, so that the effective signer/writable/owner authorization used for the account is set to an attacker-chosen or inconsistent value.
- Invariant to test: no account may be mutated, reassigned, closed, or debited without its authority signing
- Expected Immunefi impact: Critical. Missing or forgeable signer, writable, ownership, or authority checks in runtime, built-in programs, or CPI let an unprivileged caller mutate, close, reassign, or drain an account whose authority never approved it.
- Fast validation: add a focused Rust unit/fuzz test on `into_address_loader_error` in `runtime/src/bank/address_lookup_table.rs` asserting the call rejects a missing/forged signer.
