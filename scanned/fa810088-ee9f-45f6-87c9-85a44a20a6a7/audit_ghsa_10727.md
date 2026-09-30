# [C] Zebra Vulnerable to Consensus Divergence in Transparent Sighash Hash-Type Handling

## Summary
Severity: Critical
Advisory: GHSA-8m29-fpq5-89jj
CVE: CVE-2026-41583
CWE: CWE-573
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-8m29-fpq5-89jj
Type: github-advisory

## Affected
- crates.io: `zebrad` — affected >=0 <4.3.1
- crates.io: `zebra-script` — affected >=0 <5.0.2

## Details
# CVE-2026-41583: Consensus Divergence in Transparent Sighash Hash-Type Handling

## Summary

After a refactoring, Zebra failed to validate a consensus rule that restricted the possible values of sighash hash types for V5 transactions which were enabled in the NU5 network upgrade. Zebra nodes could thus accept and eventually mine a block that would be considered invalid by zcashd nodes, creating a consensus split between Zebra and zcashd nodes.

In a similar vein, for V4 transactions, Zebra mistakenly used the "canonical" hash type when computing the sighash while zcashd (correctly per the spec) uses the raw value, which could also crate a consensus split.

## Severity

**Critical** - This is a Consensus Vulnerability that could allow a malicious party to induce network partitioning, service disruption, and potential double-spend attacks against affected nodes.

Note that the impact is currently alleviated by the fact that currently most miners run `zcashd`.

## Affected Versions

All Zebra versions prior to version 4.3.1. (Some older versions are not impacted but are no longer supported by the network.)

## Description

Verification of transparent transactions inherits the Bitcoin Script verification code in C++. Since it is consensus-critical, this code was called from Zebra through foreign function interface (FFI). That interface was clunky because it required parsing the whole transaction in C++ code, which would then pull Rust libraries which could get in conflict with Zebra code. A refactoring was done so that only the verification itself was done in C++, and the rest done by Rust code, using a callback. However, in this refactoring, it was not noticed that a particular consensus rule - only accepting known hash types in transparent transaction signatures - was being enforced in C++ code and thus had to be enforced by the Rust caller.

An attacker could exploit this by:

- Submitting a V4 or V5 transaction with an invalid hash type
- The V5 transaction would be accepted by Zebra nodes but not by `zcashd` nodes (and vice-versa for V4), creating a consensus split in the network.

## Impact

**Consensus Failure**

- **Attack Vector:** Network.
- **Effect:** Network partition/consensus split.
- **Scope:** Any Zebra affected Zebra node

## Fixed Versions

This issue is fixed in Zebra 4.3.1.

The fix adds the consensus check in the caller of the C++ verification code. It also uses the raw hash type for V4 sighash computations.

## Mitigation

Users should upgrade to Zebra 4.3.1 or later immediately.

There are no known workarounds for this issue. Immediate upgrade is the only way to ensure the node remains on the correct consensus path and is protected against malicious chain forks.

## Credits

Thanks Alex “Scalar” Sol for finding and reporting the issue, and to @sangsoo-osec who independently found the same issue and demonstrated that the V4 variant was also exploitable.

## References
- https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8m29-fpq5-89jj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41583
- https://github.com/ZcashFoundation/zebra/commit/1f605eca5c55e3b65229fa01a97d9aa84fd37447
- https://github.com/ZcashFoundation/zebra
