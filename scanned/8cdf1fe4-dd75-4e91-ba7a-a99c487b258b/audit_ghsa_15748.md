# [H] Studio 42 elFinder vulnerable to Incorrect Access Control

## Summary
Severity: High
Advisory: GHSA-3h9f-mm2x-4j58
CVE: CVE-2024-38909
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-30
Source: https://github.com/advisories/GHSA-3h9f-mm2x-4j58
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0

## Details
Studio 42 elFinder 2.1.64 is vulnerable to Incorrect Access Control. Copying files with an unauthorized extension between server directories allows an arbitrary attacker to expose secrets, perform RCE, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38909
- https://github.com/B0D0B0P0T/CVE/blob/main/CVE-2024-38909
- https://github.com/Studio-42/elFinder
- http://elfinder.com
