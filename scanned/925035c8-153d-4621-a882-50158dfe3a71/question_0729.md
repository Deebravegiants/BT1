# Q0729: unpack-u16 via collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the three `price-feeds` buffers and their order, drive `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) — which unpacks eight u16 curve fields from one packed word — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `unpack-u16` touches, run `collateral-add` with the three `price-feeds` buffers and their order, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
