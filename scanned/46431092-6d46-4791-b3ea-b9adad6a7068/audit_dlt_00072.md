# [C] Zebra Transparent SIGHASH_SINGLE Corresponding-Output Handling Diverges From zcashd

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-05-02
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-cwfq-rfcr-8hmp
Type: github-advisory

## Details
# `Zebra` Transparent `SIGHASH_SINGLE` Corresponding-Output Handling Diverges From `zcashd`

### Summary
For V5+ transparent spends, `Zebra` and `zcashd` disagree on the same consensus rule: `SIGHASH_SINGLE` must fail when the input index has no corresponding output. `zcashd` treats this as consensus-invalid under ZIP-244, while `Zebra`'s transparent verification path computes a digest for the missing-output case instead of failing.

The result is a direct block-validity split. A malformed V5 transparent transaction can be accepted by `Zebra`, retained in `Zebra`'s mempool, selected into `Zebra` `getblocktemplate`, mined into a block, and then rejected by `zcashd`.

### Details
Validated code revisions used during analysis:

- `zcashd`: `2c63e9aa08cb170b0feb374161bea94720c3e1f5`
- `Zebra`: `a905fa19e3a91c7b4ead331e2709e6dec5db12cb`

Scope note:

- earlier triage material grouped pre-V5 and V5 behavior together;
- re-execution on the pinned revisions did not reproduce the claimed pre-V5 / V4 reject-side behavior;
- this advisory therefore covers the V5+ / ZIP-244 variant only.

`zcashd` side:

- Transparent scripts in blocks are checked through `TransactionSignatureChecker::CheckSig()` and `SignatureHash()`: [`zcash/src/script/interpreter.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/script/interpreter.cpp#L1386-L1407).
- In the ZIP-244 branch, `SignatureHash()` explicitly throws when `SIGHASH_SINGLE` or `SIGHASH_SINGLE|ANYONECANPAY` is used with `nIn >= txTo.vout.size()`: [`zcash/src/script/interpreter.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/script/interpreter.cpp#L1221-L1259).
- `CheckSig()` catches that exception and returns `false`, causing the transparent script to fail.

`Zebra` side:

- V5 transparent inputs route into the same FFI-based transparent script verifier used for block validation: [`zebra/zebra-consensus/src/transaction.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-consensus/src/transaction.rs#L989-L1098).
- `Zebra` converts the decoded hash type and asks its Rust sighash engine for a digest without adding the corresponding-output pre-check that `zcashd` enforces first: [`zebra/zebra-script/src/lib.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-script/src/lib.rs#L160-L175), [`zebra/zebra-chain/src/primitives/zcash_primitives.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-chain/src/primitives/zcash_primitives.rs#L307-L343).
- `Zebra` forwards canonical `SIGHASH_SINGLE` into the Rust ZIP-244 implementation.
- In that implementation, when `input.index() >= bundle.vout.len()`, the code uses `transparent_outputs_hash::<TxOut>(&[])` instead of erroring: [`zcash_primitives/src/transaction/sighash_v5.rs`](https://github.com/zcash/librustzcash/blob/c3425f9c3c7f6deb20720bb78b18f35fbbed8edd/zcash_primitives/src/transaction/sighash_v5.rs#L101-L107), [`zcash_primitives/src/transaction/sighash_v5.rs`](https://github.com/zcash/librustzcash/blob/c3425f9c3c7f6deb20720bb78b18f35fbbed8edd/zcash_primitives/src/transaction/sighash_v5.rs#L131-L139).

Why this is exploitable:

- the malformed transaction only needs fewer transparent outputs than inputs;
- the attacker signs the digest that `Zebra` computes for the missing-output case;
- `Zebra` then sees a valid transparent signature, while `zcashd` never reaches the same digest because it fails first.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-cwfq-rfcr-8hmp_
