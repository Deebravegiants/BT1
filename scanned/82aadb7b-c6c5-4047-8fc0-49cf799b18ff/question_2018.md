# Q2018: next-index via redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) have the same quantity scaled twice by two contracts that round differently? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `next-index` returns is identical in both runs; a divergence confirms the finding.
