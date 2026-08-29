# Q1620: debt-preview via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the seized zToken amount that is immediately redeemed reach `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) in a state where it count one deposit as backing for two simultaneous claims? Given that it computes cumulative debt from `principal-scaled` and the FORWARD index, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the seized zToken amount that is immediately redeemed across its boundary values through `liquidate-redeem` in simnet and assert `debt-preview` never returns a value that breaks the invariant.
