# [M] vercel/serve allows access to restricted files if filename is URL encoded.

## Summary
Severity: Medium
Advisory: GHSA-5rc4-8qqh-vq7f
CVE: CVE-2018-3718
CWE: CWE-177
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-5rc4-8qqh-vq7f
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <6.5.2

## Details
serve node module suffers from Improper Handling of URL Encoding by permitting access to ignored files if a filename is URL encoded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3718
- https://hackerone.com/reports/308721
- https://github.com/vercel/serve
