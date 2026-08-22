# Q5120: calculate_non_circulating_supply: lamport accounting break

## Question
In `runtime/src/non_circulating_supply.rs`, can an unprivileged attacker who can submit a crafted transaction touching the affected accounts attacker-chosen inputs drive the arithmetic in `calculate_non_circulating_supply` (near line 15) to under/over-count lamports, fees, or rent so total balances change, breaking the invariant that total lamports are conserved and fees/rent are accounted exactly once, corrupting the pre/post lamport (or fee/rent) balance total across the affected accounts?

## Target
- File/function: `runtime/src/non_circulating_supply.rs` :: `calculate_non_circulating_supply` (around line 15)
- Entrypoint: Transaction / instruction execution inside the bank — attacker can submit a crafted transaction touching the affected accounts
- Attacker controls: instruction data, account set, nonce, fee payer, and program invocations
- Exploit idea: Can attacker-chosen inputs drive the arithmetic in `calculate_non_circulating_supply` (near line 15) to under/over-count lamports, fees, or rent so total balances change, so that the pre/post lamport (or fee/rent) balance total across the affected accounts is set to an attacker-chosen or inconsistent value.
- Invariant to test: total lamports are conserved and fees/rent are accounted exactly once
- Expected Immunefi impact: Critical. Lamport arithmetic, rent, fee, rebate, or balance accounting can be made to under- or over-count so that total lamports are minted, burned, or silently moved between accounts across an instruction, transaction, or block boundary.
- Fast validation: add a focused Rust unit/fuzz test on `calculate_non_circulating_supply` in `runtime/src/non_circulating_supply.rs` asserting sum(lamports) before == after across the call.
