# [C] Fickling has Static Analysis Bypass via Incomplete Dangerous Module Blocklist

## Summary
Severity: Critical
Advisory: CVE-2026-22609
Aliases: GHSA-q5qq-mvfm-j35x, PYSEC-2026-1372
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22609
Type: osv

## Details
Fickling is a Python pickling decompiler and static analyzer. Prior to version 0.1.7, the unsafe_imports() method in Fickling's static analyzer fails to flag several high-risk Python modules that can be used for arbitrary code execution. Malicious pickles importing these modules will not be detected as unsafe, allowing attackers to bypass Fickling's primary static safety checks. This issue has been patched in version 0.1.7.

## References
- https://github.com/trailofbits/fickling/releases/tag/v0.1.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22609.json
- https://github.com/trailofbits/fickling/security/advisories/GHSA-q5qq-mvfm-j35x
- https://nvd.nist.gov/vuln/detail/CVE-2026-22609
- https://github.com/trailofbits/fickling/commit/29d5545e74b07766892c1f0461b801afccee4f91
- https://github.com/trailofbits/fickling/commit/9a2b3f89bd0598b528d62c10a64c1986fcb09f66
- https://github.com/trailofbits/fickling/commit/b793563e60a5e039c5837b09d7f4f6b92e6040d1
- https://github.com/trailofbits/fickling/commit/eb299b453342f1931c787bcb3bc33f3a03a173f9
