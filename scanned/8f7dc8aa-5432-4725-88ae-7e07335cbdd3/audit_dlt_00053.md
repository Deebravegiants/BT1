# [C] P2SH Sigop Undercount Not Correctly Fixed

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-06-01
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2prc-cj5x-4443
Type: github-advisory

## Details
### Am I affected

You are affected if:

- You run zebrad version v4.5.0 (note that older versions have other vulnerabilites)
- Your node validates blocks on mainnet, testnet, or any network where both Zebra and zcashd nodes participate.

All default configurations are affected. No feature flags, non-default settings, or special build options are required.

### Summary

After https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gf9r-m956-97qx, Zebra's P2SH sigop counter counts the redeem script with the legacy sigop function (`GetSigOpCount(false)`) instead of zcashd's accurate P2SH mode (`GetSigOpCount(true)`). A `CHECKMULTISIG` preceded by `OP_1` through `OP_16` is over-counted as 20 sigops instead of its true key count (1–16). This produces a consensus divergence: Zebra rejects blocks that zcashd accepts when Zebra's inflated count crosses the block-wide `MAX_BLOCK_SIGOPS = 20,000` threshold but the true count does not.

An attacker needs no mining capability. Broadcasting valid P2SH spends whose redeem scripts use low-threshold multisig is sufficient; once any miner includes enough of them in a block, Zebra validators reject a block the rest of the network accepts, splitting Zebra off the chain.

### Details

The P2SH sigop counter at `zebra-script/src/lib.rs` counts the extracted redeem script with `interpreter.legacy_sigop_count_script(&script::Code(redeemed_bytes))`. That FFI entry point (`libzcash_script 0.1.0`) wraps `zcash_script_legacy_sigop_count_script` (`zcash_script.cpp:28-34`), which calls `CScript::GetSigOpCount(false)` — the legacy, non-P2SH counting mode.

zcashd's P2SH path (`GetP2SHSigOpCount` → `CScript::GetSigOpCount(const CScript&)`, `script.cpp:176-199`) extracts the redeem script and counts it with `GetSigOpCount(true)`. The flag changes only `CHECKMULTISIG`/`CHECKMULTISIGVERIFY` (`script.cpp:152-174`): accurate mode counts the preceding `OP_1`–`OP_16` as 1–16, while legacy mode always counts 20.

The P2SH count feeds block validation: `CachedFfiTransaction::p2sh_sigops()` → `p2sh_sigop_count()` is added to the legacy sigop total in `zebra-consensus/src/transaction.rs` and checked against `MAX_BLOCK_SIGOPS = 20,000` in `zebra-consensus/src/block.rs`.

A redeem script `OP_1 <pubkey> OP_1 OP_CHECKMULTISIG` produces: Zebra = 20, zcashd = 1. A block with 1,001 such P2SH spends yields ≈ 20,020 sigops on Zebra against ≈ 1,001 on zcashd — crossing the 20,000 threshold on Zebra's side only.

### Patches

Patched in Zebra `4.5.1`. We switched back to the Rust implementation and fixed the discrepancy that originally caused https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gf9r-m956-97qx.

### Workarounds

There is no configuration-level workaround. All Zebra nodes validating blocks on a network shared with zcashd are affected. Upgrade as soon as the patched version is available.

### Impact

A chain split between Zebra and zcashd validators. The attacker broadcasts spending transactions referencing P2SH outputs whose redeem scripts use a low-threshold multisig form (e.g. `OP_1 <pubkey> OP_1 OP_CHECKMULTISIG`). When any miner — including an honest zcashd miner — includes enough of them in a block (≈ 1,000+ such inputs), the block's true sigop count stays under `MAX_BLOCK_SIGOPS` so zcashd accepts it, but Zebra's inflated count exceeds 20,000 and Zebra rejects it with `TooManyTransparentSignatureOperations`. Zebra validators stall at that height while the rest of the network advances, and every subsequent block extending the canonical tip is also rejected by Zebra.

Triggering the split needs neither a malicious miner nor adversarial intent: a block carrying enough ordinary low-threshold multisig P2SH spends is sufficient. The attacker needs no mining capability, RPC access, or special privileges; the cost is the transaction fees for the funding and spending transactions.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2prc-cj5x-4443_
