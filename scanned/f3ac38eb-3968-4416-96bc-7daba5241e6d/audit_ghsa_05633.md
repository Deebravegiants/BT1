# [M] Nu Html Checker (vnu) contains a Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fccg-7w3p-w66f
CVE: CVE-2025-15104
CWE: CWE-918
Ecosystem: Maven, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-fccg-7w3p-w66f
Type: github-advisory

## Affected
- Maven: `nu.validator:validator` — affected >=0
- npm: `vnu-jar` — affected >=0

## Details
Nu Html Checker (validator.nu) contains a restriction bypass that allows remote attackers to make the server perform arbitrary HTTP/HTTPS requests to internal resources, including localhost services. While the validator implements hostname-based protections to block direct access to localhost and 127.0.0.1, these controls can be bypassed using DNS rebinding techniques or domains that resolve to loopback addresses.This issue affects The Nu Html Checker (vnu): latest (commit 23f090a11bab8d0d4e698f1ffc197a4fe226a9cd).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15104
- https://fluidattacks.com/advisories/europe
- https://github.com/validator/validator
