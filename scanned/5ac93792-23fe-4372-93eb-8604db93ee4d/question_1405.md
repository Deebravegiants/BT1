# Q1405: remove_liquidity can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `remove_liquidity` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Pools` / `LP issuance`?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::remove_liquidity
- Entrypoint: signed extrinsic `remove_liquidity`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.
