# Q1139: Withdrawal validation can use stale account state in validateRefScriptSize

## Question
Can an unprivileged attacker exercise `validateRefScriptSize` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs` via the stated entrypoint and trigger withdrawal and account draining stale state? The investigation should test whether withdrawal validation, account draining, and certificate processing consult different snapshots of account state, causing incorrect withdrawal acceptance, rejection, or final balance.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs / validateRefScriptSize
- Entrypoint: Submit a transaction combining withdrawals with certificates that create, drain, or remove the same reward account.
- Attacker controls: Withdrawals map, account credential, certificates, certificate order, fee, witnesses, and transaction validity interval.
- Exploit idea: Check whether withdrawal validation, account draining, and certificate processing consult different snapshots of account state, causing incorrect withdrawal acceptance, rejection, or final balance.
- Invariant to test: Value conservation: consumed value plus withdrawals plus minted value must equal produced value plus fees plus deposits plus treasury/reserve movement under the era rules.
- Expected Cardano/Intersect impact: Potential Medium if an unprivileged user can trigger incorrect fees, deposits, refunds, rewards, withdrawals, treasury movement, or validation limits without full chain split.
- Fast validation: Build a minimal sequence of transactions or certificates around the boundary condition and assert deposits, refunds, withdrawals, and UTxO state after each step.
