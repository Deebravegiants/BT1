# [H] Finalized address balance credit-first overflow on consensus-valid blocks

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52738
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-w834-cf6p-9m9w
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node processes blocks on any Zcash network.

### Summary

The finalized transparent address balance writer processes all newly-created outputs (credits) before processing spent outputs (debits) within the same block. A consensus-valid block containing a long chain of same-address transparent self-spends can cause the intermediate per-address balance during the credit pass to exceed `MAX_MONEY`, triggering a panic in the finalized state writer.

Because the triggering block is consensus-valid (zcashd accepts it), the panic recurs on restart when the node re-encounters the same block. This creates a persistent chain halt that can only be resolved by a software patch.

### Details

The finalized state writer at `zebra-state/src/service/finalized_state/zebra_db/transparent.rs` iterates all transaction outputs in a block and credits them to per-address balances before iterating inputs and debiting spent outputs. When a block contains many transparent self-spends to the same address, the intermediate credit-only balance can exceed the `MAX_MONEY` supply cap even though the final net balance (credits minus debits) is valid.

The code panics on the intermediate overflow via `.expect()` on the balance addition. Under Zebra's `panic = "abort"` release profile, this terminates the process. On restart, the node re-downloads and re-processes the same consensus-valid block, triggering the same panic.

An attacker with approximately 1,100–2,100 ZEC and mining capability can construct a block that permanently halts all Zebra nodes. The attacker recovers their capital (the self-spends return funds to the same address), so the net cost is the mining effort only.

### Patches

Patched in Zebra 4.4.2. The fix processes credits and debits together per transaction rather than all credits then all debits, matching zcashd's approach.

### Workarounds

No workaround is available. Upgrade to Zebra 4.4.2.

### Impact

A single consensus-valid mined block can permanently halt all Zebra nodes on the network. The halt persists across restarts. Recovery requires deploying a patched version. Downstream consumers (light wallets, exchanges, mining infrastructure) lose service for the duration of the halt.

### Credit

Reported by `@sangsoo-osec`.

### References

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-w834-cf6p-9m9w_
