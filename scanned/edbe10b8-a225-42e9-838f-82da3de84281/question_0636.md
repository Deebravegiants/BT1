# Q0636: convert-to-assets-preview via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it prices a redemption against `total-assets-preview` and `total-supply-preview`, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `convert-to-assets-preview` never returns a value that breaks the invariant.
