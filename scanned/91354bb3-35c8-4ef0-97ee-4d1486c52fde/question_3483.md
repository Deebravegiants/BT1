# Q3483: debt-preview via redeem: count one deposit as backing for two simultaneous claims

## Question
`debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) computes cumulative debt from `principal-scaled` and the FORWARD index. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `amount` of shares burned, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `debt-preview` touches, run `redeem` with `amount` of shares burned, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
