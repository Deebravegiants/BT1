# Q2160: accrue-and-cache via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `min-out` reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it credit one side of an accounting pair without the other? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-out` across its boundary values through `redeem` in simnet and assert `accrue-and-cache` never returns a value that breaks the invariant.
