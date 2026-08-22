# Q1418: update_with_newly_valid_ancestor: authority bypass

## Question
In `core/src/consensus/heaviest_subtree_fork_choice.rs`, can an unprivileged attacker who can submit a transaction / CPI invoking the affected program path an unprivileged attacker reach `update_with_newly_valid_ancestor` (near line 1274) and mutate, close, reassign, or debit an account whose authority never signed, breaking the invariant that no account may be mutated, reassigned, closed, or debited without its authority signing, corrupting the effective signer/writable/owner authorization used for the account?

## Target
- File/function: `core/src/consensus/heaviest_subtree_fork_choice.rs` :: `update_with_newly_valid_ancestor` (around line 1274)
- Entrypoint: Consensus / replay of blocks and votes — attacker can submit a transaction / CPI invoking the affected program path
- Attacker controls: block contents, vote transactions, slot ancestry, and fork weights
- Exploit idea: Can an unprivileged attacker reach `update_with_newly_valid_ancestor` (near line 1274) and mutate, close, reassign, or debit an account whose authority never signed, so that the effective signer/writable/owner authorization used for the account is set to an attacker-chosen or inconsistent value.
- Invariant to test: no account may be mutated, reassigned, closed, or debited without its authority signing
- Expected Immunefi impact: Critical. Missing or forgeable signer, writable, ownership, or authority checks in runtime, built-in programs, or CPI let an unprivileged caller mutate, close, reassign, or drain an account whose authority never approved it.
- Fast validation: add a focused Rust unit/fuzz test on `update_with_newly_valid_ancestor` in `core/src/consensus/heaviest_subtree_fork_choice.rs` asserting the call rejects a missing/forged signer.
