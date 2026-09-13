# [M] rz-libdemangle: Out of bound read in rust demangler

## Summary
Severity: Medium
Advisory: CVE-2026-45612
Aliases: GHSA-4p92-mfjf-qvrc
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-45612
Type: osv

## Details
rz-libdemangle is a Rizin library for demangling symbols. Prior to 6bf56d3, the Rust demangler in src/rust/rust_v0.c can perform an out-of-bounds read when the demangler structure is not yet initialized. This issue is fixed in commit 6bf56d3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45612.json
- https://github.com/rizinorg/rz-libdemangle/security/advisories/GHSA-4p92-mfjf-qvrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45612
- https://github.com/rizinorg/rz-libdemangle/commit/6bf56d32b32547ae4cb069ccfc2d2b6c7b63a4cb
- https://github.com/rizinorg/rz-libdemangle/pull/83
