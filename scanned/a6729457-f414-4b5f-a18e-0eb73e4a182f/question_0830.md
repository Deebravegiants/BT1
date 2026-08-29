# Q0830: status-multi via collateral-add: mint shares whose backing was never received

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling `amount`, can an unprivileged attacker make `status-multi` (mainnet/contracts/registry/v0-assets.clar:163) mint shares whose backing was never received? `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:163` -> `status-multi`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `status-multi` returns is identical in both runs; a divergence confirms the finding.
