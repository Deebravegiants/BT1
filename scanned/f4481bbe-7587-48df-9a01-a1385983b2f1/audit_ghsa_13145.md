# [H] blurhash panics on parsing crafted inputs

## Summary
Severity: High
Advisory: GHSA-cxvp-82cq-57h2
CVE: CVE-2023-42447
CWE: CWE-1284, CWE-392
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-cxvp-82cq-57h2
Type: github-advisory

## Affected
- crates.io: `blurhash` — affected >=0.1.1 <0.2.0

## Details
### Impact
The blurhash parsing code may panic due to multiple panic-guarded out-of-bounds accesses on untrusted input.

In a typical deployment, this may get triggered by feeding a maliciously crafted blurhashes over the network. These may include:
- UTF-8 compliant strings containing multi-byte UTF-8 characters

### Patches
The patches will be released under version 0.2.0, which requires user intervention because of slight API churn.

### Workarounds
n.a.

### References
n.a.

## References
- https://github.com/whisperfish/blurhash-rs/security/advisories/GHSA-cxvp-82cq-57h2
- https://nvd.nist.gov/vuln/detail/CVE-2023-42447
- https://github.com/whisperfish/blurhash-rs
- https://github.com/whisperfish/blurhash-rs/releases/tag/v0.2.0
