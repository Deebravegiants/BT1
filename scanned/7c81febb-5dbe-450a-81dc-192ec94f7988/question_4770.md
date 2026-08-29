# Q4770: collateral-remove via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) destroy value through a truncation the opposite operation does not restore? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
