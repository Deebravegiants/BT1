# [H] Aim vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-38r9-3j52-h92v
CVE: CVE-2024-7760
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-38r9-3j52-h92v
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
aimhubio/aim version 3.22.0 contains a Cross-Site Request Forgery (CSRF) vulnerability in the tracking server. The vulnerability is due to overly permissive CORS settings, allowing cross-origin requests from all origins. This enables CSRF attacks on all endpoints of the tracking server, which can be chained with other existing vulnerabilities such as remote code execution, denial of service, and arbitrary file read/write.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7760
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/2038df5f-4829-4040-8573-67bf9bb89229
