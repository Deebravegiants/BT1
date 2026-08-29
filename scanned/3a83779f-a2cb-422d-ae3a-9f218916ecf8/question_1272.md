# Q1272: resolve-dia via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the seized zToken amount that is immediately redeemed reach `resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) in a state where it count one deposit as backing for two simultaneous claims? Given that it derives a (string-ascii 32) key from a (buff 32) ident, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the seized zToken amount that is immediately redeemed across its boundary values through `liquidate-redeem` in simnet and assert `resolve-dia` never returns a value that breaks the invariant.
