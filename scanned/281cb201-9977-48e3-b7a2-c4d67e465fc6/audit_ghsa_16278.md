# [H] October CMS Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-gcgj-qh8p-57hm
CVE: CVE-2023-25365
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-gcgj-qh8p-57hm
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0

## Details
Cross Site Scripting vulnerability found in October CMS v.3.2.0 allows local attacker to execute arbitrary code via the file type .mp3

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25365
- https://cupc4k3.medium.com/cve-2023-25365-xss-via-file-upload-bypass-ddf4d2a106a7
- https://github.com/octobercms/october
