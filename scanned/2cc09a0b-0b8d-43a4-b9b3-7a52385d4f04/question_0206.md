# Q0206: resolve via borrow: mint shares whose backing was never received

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `resolve` (mainnet/contracts/registry/v0-egroup.clar:360) mint shares whose backing was never received? `resolve` selects the efficiency group for a position mask, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:360` -> `resolve`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve` selects the efficiency group for a position mask. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `receiver`, including a contract principal varied, and assert that the value `resolve` returns is identical in both runs; a divergence confirms the finding.
