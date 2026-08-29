# Q4278: get-notional-evaluation via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) destroy value through a truncation the opposite operation does not restore? `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `get-notional-evaluation` never returns a value that breaks the invariant.
