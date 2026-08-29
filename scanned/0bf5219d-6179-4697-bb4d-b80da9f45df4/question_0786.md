# Q0786: calc-index-next via call-ststx-ratio: mint shares whose backing was never received

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) mint shares whose backing was never received? `calc-index-next` applies a multiplier to the current index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `call-ststx-ratio` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the ratio is fetched before or after other state changes in the block across its boundary values through `call-ststx-ratio` in simnet and assert `calc-index-next` never returns a value that breaks the invariant.
