# [M] PYSEC-2024-205

## Summary
Severity: Medium
Advisory: PYSEC-2024-205
Aliases: CVE-2024-24564, GHSA-4hwq-4cpm-8vmx
Ecosystem: PyPI
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/PYSEC-2024-205
Type: osv

## Affected
- PyPI: `vyper` — affected >=0 <3d9c537142fb99b2672f21e2057f5f202cde194f, >=0 <0.4.0

## Details
Vyper is a pythonic Smart Contract Language for the ethereum virtual machine. When using the built-in `extract32(b, start)`, if the `start` index provided has for side effect to update `b`, the byte array to extract `32` bytes from, it could be that some dirty memory is read and returned by `extract32`. This vulnerability is fixed in 0.4.0.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-4hwq-4cpm-8vmx
- https://github.com/vyperlang/vyper/security/advisories/GHSA-4hwq-4cpm-8vmx
- https://github.com/vyperlang/vyper/commit/3d9c537142fb99b2672f21e2057f5f202cde194f
- https://github.com/advisories/GHSA-4hwq-4cpm-8vmx
