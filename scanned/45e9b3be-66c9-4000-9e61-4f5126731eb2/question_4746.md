# Q4746: status-multi via collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the position's existing collateral and debt composition, can an unprivileged attacker make `status-multi` (mainnet/contracts/registry/v0-assets.clar:163) destroy value through a truncation the opposite operation does not restore? `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:163` -> `status-multi`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the position's existing collateral and debt composition across its boundary values through `collateral-add` in simnet and assert `status-multi` never returns a value that breaks the invariant.
