# Q3552: refresh via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls remaining zToken collateral whose price moves with the redeem reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz remaining zToken collateral whose price moves with the redeem across its boundary values through `collateral-remove-redeem` in simnet and assert `refresh` never returns a value that breaks the invariant.
