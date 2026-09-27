# [M] olm dependency deprecation: CVE-2022-39255 and CVE-2024-45193

## Summary
Severity: Medium
Advisory: GHSA-wchh-9x6h-7f6p
CWE: CWE-1395
Ecosystem: PyPI
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-wchh-9x6h-7f6p
Type: github-advisory

## Affected
- PyPI: `matrix-commander` — affected >=0

## Details
### Problem

Multiple vulnerabilities were disclosed in 2024 affecting libolm (Olm): AES timing / side‑channel, Ed25519 signature malleability, and timing leaks in base64 decoding; several CVEs were assigned. Patches and mitigations were published; maintainers recommend upgrading to fixed versions. In addition, a 2022 “Olm/Megolm protocol confusion” advisory affecting some SDKs was critical and required client-side fixes. Use patched versions of libolm and up-to-date Matrix SDKs; avoid unpatched clients/servers.

Olm is a dependency of `matrix-commander` (Python version, not Rust version).

WARNING:

Due to cryptographic [olm dependency deprecation](https://github.com/8go/matrix-commander/issues/204#issuecomment-3523986979), this program is cryptographically unsafe to use until https://github.com/matrix-nio/matrix-nio/pull/555 is merged. Good news: https://github.com/8go/matrix-commander-rs is a Rust alternative not having this issue.


### References
- CVE-2022-39255
- CVE-2024-45193
- https://soatok.blog/2024/08/14/security-issues-in-matrixs-olm-library/
- https://nvd.nist.gov/nvd.cfm?cvename=CVE-2024-45193
- https://github.com/matrix-org/matrix-ios-sdk/security/advisories/GHSA-hw6g-j8v6-9hcm

### Workarounds
- use the Rust version: https://github.com/8go/matrix-commander-rs 

### Severity:

Medium

CVE-2022-39255 — MEDIUM (NVD/MITRE lists CVSS base score 5.x — treated as Medium).

CVE-2024-45193 — MEDIUM (NVD shows CVSS 3.1 base score ~4.3 — Medium)

## References
- https://github.com/8go/matrix-commander/security/advisories/GHSA-wchh-9x6h-7f6p
- https://github.com/8go/matrix-commander/issues/204#issuecomment-3523986979
- https://github.com/matrix-nio/matrix-nio/pull/555
- https://github.com/matrix-nio/matrix-nio/commit/71a1c808bc2ae6ea2a6e8effa7c11bd09796c626
- https://github.com/8go/matrix-commander
