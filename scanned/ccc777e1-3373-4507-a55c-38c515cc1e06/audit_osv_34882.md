# [M] fontTools is Vulnerable to Arbitrary File Write and XML injection in fontTools.varLib

## Summary
Severity: Medium
Advisory: CVE-2025-66034
Aliases: GHSA-768j-98cg-p3fv, PYSEC-2026-1389
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:L)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66034
Type: osv

## Details
fontTools is a library for manipulating fonts, written in Python. In versions from 4.33.0 to before 4.60.2, the fonttools varLib (or python3 -m fontTools.varLib) script has an arbitrary file write vulnerability that leads to remote code execution when a malicious .designspace file is processed. The vulnerability affects the main() code path of fontTools.varLib, used by the fonttools varLib CLI and any code that invokes fontTools.varLib.main(). This issue has been patched in version 4.60.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66034.json
- https://github.com/fonttools/fonttools/security/advisories/GHSA-768j-98cg-p3fv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66034
- https://github.com/fonttools/fonttools/commit/a696d5ba93270d5954f98e7cab5ddca8a02c1e32
