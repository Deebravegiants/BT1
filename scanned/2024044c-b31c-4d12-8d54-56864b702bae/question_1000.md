# Q1000: try_borrow_instruction_account breaks lamport conservation (instruction.rs)

## Question
Can an unprivileged attacker entering through deploying an attacker-authored sBPF program and invoking it with crafted instruction data and account lists reach `try_borrow_instruction_account` in `transaction-context/src/instruction.rs` with an account owned by a program the caller controls, with attacker-chosen data, and make the lamports `try_borrow_instruction_account` removes differ from the lamports it credits, so that the invariant "Sum of lamports before and after the operation is equal, except for the explicit fee/rent burn." breaks and the result is Loss of Funds?

## Target
- File/function: `transaction-context/src/instruction.rs` -> `try_borrow_instruction_account()` (around line 206)
- Entrypoint: deploying an attacker-authored sBPF program and invoking it with crafted instruction data and account lists
- Attacker controls: an account owned by a program the caller controls, with attacker-chosen data
- Exploit idea: Drive `try_borrow_instruction_account` so the lamports it removes and the lamports it adds differ, minting or destroying value outside the inflation schedule.
- Invariant to test: Sum of lamports before and after the operation is equal, except for the explicit fee/rent burn.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Property test around `try_borrow_instruction_account`: assert `sum_lamports_before == sum_lamports_after + burned` over randomized inputs.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
