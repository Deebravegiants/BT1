# Q1580: resolve-ztoken via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `resolve-ztoken` (mainnet/contracts/market/v0-4-market.clar:343) in a state where it count one deposit as backing for two simultaneous claims? Given that it reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:343` -> `resolve-ztoken`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `ft` trait principal varied, and assert that the value `resolve-ztoken` returns is identical in both runs; a divergence confirms the finding.
