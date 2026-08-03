# Q1442: claim_swap can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `claim_swap` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `PendingSwaps` / `hashlock state`?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::claim_swap
- Entrypoint: signed extrinsic `claim_swap`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.
