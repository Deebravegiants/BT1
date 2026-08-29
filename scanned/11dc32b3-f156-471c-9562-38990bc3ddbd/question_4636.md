# Q4636: unpack-u16 via liquidate-multi: mint shares whose backing was never received

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it mint shares whose backing was never received? Given that it unpacks eight u16 curve fields from one packed word, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the trait principals supplied per entry, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
