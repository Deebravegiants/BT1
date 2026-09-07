# [M] Cross site scripting in safe-svg

## Summary
Severity: Medium
Advisory: GHSA-5h7w-hmxc-99g5
CVE: CVE-2022-1091
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-19
Source: https://github.com/advisories/GHSA-5h7w-hmxc-99g5
Type: github-advisory

## Affected
- Packagist: `darylldoyle/safe-svg` — affected >=0 <1.9.10

## Details
The sanitisation step of the Safe SVG WordPress plugin before 1.9.10 can be bypassed by spoofing the content-type in the POST request to upload a file. Exploiting this vulnerability, an attacker will be able to perform the kinds of attacks that this plugin should prevent (mainly XSS, but depending on further use of uploaded SVG files potentially other XML attacks).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1091
- https://github.com/10up/safe-svg/pull/28
- https://github.com/10up/safe-svg/commit/00cb9a86d1bff2214714557d1901ec3896564e50
- https://github.com/10up/safe-svg
- https://wpscan.com/vulnerability/4d12533e-bdb7-411f-bcdf-4c5046db13f3
