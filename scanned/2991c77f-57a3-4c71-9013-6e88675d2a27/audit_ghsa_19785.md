# [H] nossrf Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-vm77-mr48-27wj
CVE: CVE-2025-2691
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-03-23
Source: https://github.com/advisories/GHSA-vm77-mr48-27wj
Type: github-advisory

## Affected
- npm: `nossrf` — affected >=0 <1.0.4

## Details
Versions of the package nossrf before 1.0.4 are vulnerable to Server-Side Request Forgery (SSRF), where an attacker can provide a hostname that resolves to a local or reserved IP address space and bypass the SSRF protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2691
- https://security.snyk.io/vuln/SNYK-JS-NOSSRF-9510842
