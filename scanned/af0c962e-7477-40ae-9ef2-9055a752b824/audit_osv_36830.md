# [H] SumatraPDF Update MITM -> Arbitrary Code Execution

## Summary
Severity: High
Advisory: CVE-2026-25961
Aliases: GHSA-xpm2-rr5m-x96q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25961
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. In 3.5.0 through 3.5.2, SumatraPDF's update mechanism disables TLS hostname verification (INTERNET_FLAG_IGNORE_CERT_CN_INVALID) and executes installers without signature checks. A network attacker with any valid TLS certificate (e.g., Let's Encrypt) can intercept the update check request, inject a malicious installer URL, and achieve arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25961.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-xpm2-rr5m-x96q
- https://nvd.nist.gov/vuln/detail/CVE-2026-25961
