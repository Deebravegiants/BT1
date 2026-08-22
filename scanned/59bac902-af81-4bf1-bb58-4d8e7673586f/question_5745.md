# Q5745: is_signer: lamport accounting break

## Question
In `transaction-context/src/instruction_accounts.rs`, can an unprivileged attacker who can submit a crafted transaction touching the affected accounts attacker-chosen inputs drive the arithmetic in `is_signer` (near line 115) to under/over-count lamports, fees, or rent so total balances change, breaking the invariant that total lamports are conserved and fees/rent are accounted exactly once, corrupting the pre/post lamport (or fee/rent) balance total across the affected accounts?

## Target
- File/function: `transaction-context/src/instruction_accounts.rs` :: `is_signer` (around line 115)
- Entrypoint: CPI / built-in program invocation and instruction serialization — attacker can submit a crafted transaction touching the affected accounts
- Attacker controls: instruction data, account infos, CPI arguments, compute budget, and program ids
- Exploit idea: Can attacker-chosen inputs drive the arithmetic in `is_signer` (near line 115) to under/over-count lamports, fees, or rent so total balances change, so that the pre/post lamport (or fee/rent) balance total across the affected accounts is set to an attacker-chosen or inconsistent value.
- Invariant to test: total lamports are conserved and fees/rent are accounted exactly once
- Expected Immunefi impact: Critical. Lamport arithmetic, rent, fee, rebate, or balance accounting can be made to under- or over-count so that total lamports are minted, burned, or silently moved between accounts across an instruction, transaction, or block boundary.
- Fast validation: add a focused Rust unit/fuzz test on `is_signer` in `transaction-context/src/instruction_accounts.rs` asserting sum(lamports) before == after across the call.
