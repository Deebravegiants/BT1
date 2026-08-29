# Q4500: receive-tokens via collateral-remove-redeem: mint shares whose backing was never received

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls the zToken/underlying id mapping reached (the u100 sentinel branch) reach `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) in a state where it mint shares whose backing was never received? Given that it pulls an asset from a named account, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `receive-tokens` never returns a value that breaks the invariant.
