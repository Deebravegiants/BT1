# Q4236: get-available-assets via transfer: mint shares whose backing was never received

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it mint shares whose backing was never received? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the destination principal, including the market, the market-vault or the treasury across its boundary values through `transfer` in simnet and assert `get-available-assets` never returns a value that breaks the invariant.
