# [H] Avenwu Whistle Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-gg6x-448q-pqqm
CVE: CVE-2024-55500
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-10
Source: https://github.com/advisories/GHSA-gg6x-448q-pqqm
Type: github-advisory

## Affected
- npm: `whistle` — affected >=0

## Details
Cross-Site Request Forgery (CSRF) in Avenwu Whistle v.2.9.90 and before allows attackers to perform malicious API calls, resulting in the execution of arbitrary code on the victim's machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55500
- https://github.com/avwo/whistle/commit/d1b8ca275dc4e453bd2efed392c0fd4b92f73cdf
- https://github.com/avwo/whistle
- https://www.sonarsource.com/blog/never-underestimate-csrf-why-origin-reflection-is-a-bad-idea
