# [?] Gate #26816 gas-underflow fix for safe rollout (mainnet replay correctness) (#26829)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-05-29
Source: https://github.com/MystenLabs/sui/commit/197452c564debb797067e390543718537c9cfbad
Type: security-commit

## Details
Gate #26816 gas-underflow fix for safe rollout (mainnet replay correctness) (#26829)

## Summary

Stacked on #26828 (the fix). This PR adds gating so the fix can land in
`main` under proper protocol-versioning discipline while reproducing the
out-of-band mainnet hotfix bit-for-bit. **The diff here shows exactly
how the gating was applied to the pre-existing fix.**

> Review **#26828 first**; this PR's base is `mlogan-26816-fix`, so the
diff below is gating-only.

## Activation logic

```
prune = IFFW && (
    prune_address_balance_gas_payment_on_iffw()      // protocol v126, all chains — forward rollout
    || accumulator_version >= 692949576              // mainnet-only backfill (None elsewhere)
)
```

- **All chains, protocol v126+:** the new feature flag enables the fix
(clean, versioned rollout).
- **Mainnet only:** an accumulator-version backfill (ported from #26817)
additionally applies the fix at/above the recovery accumulator root
version, reproducing the mid-epoch hotfix that shipped *before* the flag
existed. This is what makes mainnet replay correct — those transactions
ran under a protocol version where the flag is off.
- **Testnet / devnet / fresh networks:** `accumulator_version` is
`None`, so the backfill is inert and behavior is governed purely by the
v126 flag.

`ExecutionOrEarlyError` becomes a struct carrying `(early_error,
accumulator_version)`. The accumulator version is populated **only for
mainnet committed execution** (`authority.rs`); `None` on every other
chain and on non-committed paths (dev-inspect, simulation, genesis,
replay tools).


_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/197452c564debb797067e390543718537c9cfbad_
