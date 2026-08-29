# [C] Zebra v4.4.0 still accepts V5 SIGHASH_SINGLE without a corresponding output

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-05-04
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-pvmv-cwg8-v6c8
Type: github-advisory

## Details
# Consensus Divergence in V5 Transparent SIGHASH_SINGLE With No Corresponding Output

## Summary

Zebra failed to enforce a ZIP-244 consensus rule for V5 transparent transactions: when an input is signed with `SIGHASH_SINGLE` and there is no transparent output at the same index as that input, validation must fail. Zebra instead asked the underlying sighash library to compute a digest, and that library produced a digest over an empty output set rather than failing. An attacker could craft a V5 transaction with more transparent inputs than outputs that Zebra accepts but `zcashd` rejects, creating a consensus split between Zebra and `zcashd` nodes.

A previous fix ([`GHSA-cwfq-rfcr-8hmp`](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-cwfq-rfcr-8hmp)) addressed a closely related case in the same area of the code, but did not cover this specific one. 

## Severity

**Critical** - This is a Consensus Vulnerability that could allow a malicious party to induce network partitioning, service disruption, and potential double-spend attacks against affected nodes.

Note that the impact is currently alleviated by the fact that currently most miners run `zcashd`.

## Affected Versions

Zebra 4.4.0.

## Description

Verification of transparent transactions inherits the Bitcoin Script verification code in C++. Since it is consensus-critical, this code is called from Zebra through a foreign function interface (FFI), with a Rust callback that computes the sighash for each input being verified.

ZIP-244 §S.2a marks two situations as consensus failure for V5 transparent signatures:

1. The signed hash type is not one of the six canonical values; and
2. The hash type is `SIGHASH_SINGLE` (alone or combined with `ANYONECANPAY`) and the input has no transparent output at the same index.

`zcashd` enforces both rules: its `SignatureHash` raises an exception, and `CheckSig` catches it and fails the script. A previous fix (`GHSA-cwfq-rfcr-8hmp`) added the first rule to Zebra's V5 sighash callback. The second rule, however, was not added — Zebra's callback forwarded the request to `librustzcash`'s ZIP-244 implementation, which handles an out-of-range `SIGHASH_SINGLE` output index by hashing an empty output set rather than refusing to produce a digest. As a result, Zebra would compute a well-defined sighash for the missing-output case and accept any signature that verified against it.

An attacker could exploit this by:

- Constructing a V5 transaction with two or more transparent inputs and fewer transparent outputs;
- Signing an input whose index has no matching `vout` entry with `SIGHASH_SINGLE` (`0x03`) or `SIGHASH_SINGLE|ANYONECANPAY` (`0x83`), using the digest Zebra computes;
- Broadcasting the transaction, or a block containing it, to the network.

Zebra would verify the transaction's transparent script and accept the transaction (and any block containing it), while `zcashd` would reject both, splitting Zebra nodes from the rest of the network.

## Impact

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-pvmv-cwg8-v6c8_
