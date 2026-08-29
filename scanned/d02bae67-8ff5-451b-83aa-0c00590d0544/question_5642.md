# Q5642: calc-multiplier-delta via repay: count one deposit as backing for two simultaneous claims

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) count one deposit as backing for two simultaneous claims? `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with the `ft` trait principal varied, and assert that the value `calc-multiplier-delta` returns is identical in both runs; a divergence confirms the finding.
