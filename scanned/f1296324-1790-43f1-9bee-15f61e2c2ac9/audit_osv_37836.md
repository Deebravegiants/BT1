# [H] Zen-C has Stack-Based Buffer Overflow in Identifier Mangling

## Summary
Severity: High
Advisory: CVE-2026-33491
Aliases: GHSA-rv74-w6q7-h8xr
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33491
Type: osv

## Details
Zen C is a systems programming language that compiles to human-readable GNU C/C11. Prior to version 0.4.4, a stack-based buffer overflow vulnerability in the Zen C compiler allows attackers to cause a compiler crash or potentially execute arbitrary code by providing a specially crafted Zen C source file (`.zc`) with excessively long struct, function, or trait identifiers. Users are advised to update to Zen C version v0.4.4 or later to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33491.json
- https://github.com/zenc-lang/zenc/security/advisories/GHSA-rv74-w6q7-h8xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33491
