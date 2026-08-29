# Q3611: vault-system-borrow via borrow: count one deposit as backing for two simultaneous claims

## Question
`vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) routes a borrow to one of six vaults by asset id. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `receiver`, including a contract principal, and assert the attacker's net token balance change is zero or negative.
