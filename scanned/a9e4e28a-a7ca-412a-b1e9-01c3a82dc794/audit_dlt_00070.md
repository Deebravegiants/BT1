# [C] Consensus Divergence in Transparent Sighash Hash-Type Handling due to Stale Buffer

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-44497
Published: 2026-05-02
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gq4h-3grw-2rhv
Type: github-advisory

## Details
# CVE-XXXX-XXXXX: Consensus Divergence in Transparent Sighash Hash-Type Handling due to Stale Buffer

## Summary

The fix for https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8m29-fpq5-89jj introduced a separate issue due to insuficient error handling of the case where the sighash type is invalid, during sighash computation. Instead of returning an error, the normal flow would resume, and the input sighash buffer would be left untouched. In scenarios where a previous signature validation could leave a valid sighash in the buffer, an invalid hash-type could be incorrectly accepted, which would create a consensus split between Zebra and zcashd nodes.

## Severity

**Critical** - This is a Consensus Vulnerability that could allow a malicious party to induce network partitioning, service disruption, and potential double-spend attacks against affected nodes.

Note that the impact is currently alleviated by the fact that currently most miners run `zcashd`.

## Affected Versions

Zebra 4.3.1

## Description

Verification of transparent transactions inherits the Bitcoin Script verification code in C++, called from Zebra through a foreign function interface (FFI) with a Rust callback that computes the sighash. The fix for  https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8m29-fpq5-89jj added the missing V5 hash-type consensus check on the Rust side, returning `None` for undefined hash types. However, the FFI bridge only writes to the C++ sighash buffer when the callback returns `Some`, and the C++ checker reads that buffer unconditionally, so the failure signal is lost.

An attacker could exploit this by:

- Constructing a transparent output spent by a script that runs a valid `OP_CHECKSIGVERIFY` immediately before an `OP_CHECKSIG` with an undefined hash type.
- The first opcode primes the C++ sighash buffer with a valid digest; the second causes Zebra's callback to return `None` while the C++ checker verifies the invalid signature against the stale digest.
- Zebra accepts the spend, zcashd rejects it, creating a consensus split in the network.

## Impact

**Consensus Failure**

- **Attack Vector:** Network.
- **Effect:** Network partition/consensus split.
- **Scope:** Any affected Zebra node, and any miner or template pipeline that relies on Zebra's validation result.

## Fixed Versions

This issue is fixed in 4.4.0.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gq4h-3grw-2rhv_
