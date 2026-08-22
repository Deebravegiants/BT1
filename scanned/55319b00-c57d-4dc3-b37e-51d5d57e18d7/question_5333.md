# Q5333: try_from: authority bypass

## Question
In `runtime-transaction/src/runtime_transaction/sdk_transactions.rs`, can an unprivileged attacker who can submit a transaction / CPI invoking the affected program path an unprivileged attacker reach `try_from` (near line 44) and mutate, close, reassign, or debit an account whose authority never signed, breaking the invariant that no account may be mutated, reassigned, closed, or debited without its authority signing, corrupting the effective signer/writable/owner authorization used for the account?

## Target
- File/function: `runtime-transaction/src/runtime_transaction/sdk_transactions.rs` :: `try_from` (around line 44)
- Entrypoint: Transaction sanitization / message parsing before scheduling — attacker can submit a transaction / CPI invoking the affected program path
- Attacker controls: raw transaction bytes, account keys, header counts, and instruction layout
- Exploit idea: Can an unprivileged attacker reach `try_from` (near line 44) and mutate, close, reassign, or debit an account whose authority never signed, so that the effective signer/writable/owner authorization used for the account is set to an attacker-chosen or inconsistent value.
- Invariant to test: no account may be mutated, reassigned, closed, or debited without its authority signing
- Expected Immunefi impact: Critical. Missing or forgeable signer, writable, ownership, or authority checks in runtime, built-in programs, or CPI let an unprivileged caller mutate, close, reassign, or drain an account whose authority never approved it.
- Fast validation: add a focused Rust unit/fuzz test on `try_from` in `runtime-transaction/src/runtime_transaction/sdk_transactions.rs` asserting the call rejects a missing/forged signer.
