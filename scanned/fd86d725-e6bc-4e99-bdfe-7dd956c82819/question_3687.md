# Q3687: oracle-last-update via collateral-add: count one deposit as backing for two simultaneous claims

## Question
`oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing call ordering within the block, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `oracle-last-update` touches, run `collateral-add` with call ordering within the block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
