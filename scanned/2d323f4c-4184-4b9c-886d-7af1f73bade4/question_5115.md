# Q5115: collateral-remove via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
`collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) decrements the map and writes the entry before `send-tokens` executes. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the trait principals supplied per entry, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `collateral-remove` touches, run `liquidate-multi` with the trait principals supplied per entry, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
