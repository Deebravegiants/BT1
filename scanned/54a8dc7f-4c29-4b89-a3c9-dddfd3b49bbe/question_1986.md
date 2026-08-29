# Q1986: status-multi via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `status-multi` (mainnet/contracts/registry/v0-assets.clar:163) have the same quantity scaled twice by two contracts that round differently? `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:163` -> `status-multi`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `debt-amount` across its boundary values through `liquidate` in simnet and assert `status-multi` never returns a value that breaks the invariant.
