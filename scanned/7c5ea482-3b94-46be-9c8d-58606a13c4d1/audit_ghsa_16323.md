# [M] Webtrees Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6w5q-79rf-7c49
CVE: CVE-2024-22723
CWE: CWE-22, CWE-31
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-6w5q-79rf-7c49
Type: github-advisory

## Affected
- Packagist: `fisharebest/webtrees` — affected >=0

## Details
Webtrees 2.1.18 is vulnerable to Directory Traversal. By manipulating the "media_folder" parameter in the URL, an attacker (in this case, an administrator) can navigate beyond the intended directory (the 'media/' directory) to access sensitive files in other parts of the application's file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22723
- https://cupc4k3.medium.com/cve-2024-22723-webtrees-vulnerability-uncovering-sensitive-data-through-path-traversal-7442e7a38b68
- https://github.com/fisharebest/webtrees
