# [H] Critical Use-After-Free in Wasmi's Linear Memory

## Summary
Severity: High
Advisory: GHSA-g4v2-cjqp-rfmq
CVE: CVE-2025-66627
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-g4v2-cjqp-rfmq
Type: github-advisory

## Affected
- crates.io: `wasmi` — affected >=0.41.0 <0.41.2
- crates.io: `wasmi` — affected >=0.42.0 <0.47.1
- crates.io: `wasmi` — affected >=0.50.0 <0.51.3
- crates.io: `wasmi` — affected >=1.0.0 <1.0.1

## Details
### Summary

A use-after-free vulnerability has been discovered in the linear memory implementation of Wasmi. This issue can be triggered by a WebAssembly module under certain memory growth conditions, potentially leading to memory corruption, information disclosure, or code execution.

### Impact

- **Confidentiality:** High – attacker-controlled memory reads possible.
- **Integrity:** High – memory corruption may allow arbitrary writes.
- **Availability:** High – interpreter crashes possible.

### Affected Versions

Wasmi `v0.41.0` through Wasmi `v1.0.0`.

### Workarounds

- Upgrade to the latest patched version of Wasmi.
- Consider limiting the maximum linear memory sizes where feasible.

### Credits

This vulnerability was discovered by **Robert T. Morris (RTM)**.

## References
- https://github.com/wasmi-labs/wasmi/security/advisories/GHSA-g4v2-cjqp-rfmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-66627
- https://github.com/wasmi-labs/wasmi/commit/0e6f0d2a8325602c58d6a53ce1c0e6045eb6a490
- https://github.com/wasmi-labs/wasmi
