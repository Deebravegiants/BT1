# [H] rdiffweb CSRF vulnerability in profile's SSH keys can lead to unauthorized access

## Summary
Severity: High
Advisory: GHSA-vq4h-xrwc-m639
CVE: CVE-2022-3221
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-vq4h-xrwc-m639
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.3

## Details
rdiffweb prior to 2.4.3 is vulnerable to Cross-Site Request Forgery (CSRF). While adding SSH public keys to the profile, the server accepts the GET request, which results in adding an SSH public key to the profile and leads to unauthorized access to the system and backups. Version 2.4.3 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3221
- https://github.com/ikus060/rdiffweb/commit/9125f5a2d918fed0f3fc1c86fa94cd1779ed9f73
- https://github.com/advisories/GHSA-vq4h-xrwc-m639
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-278.yaml
- https://huntr.dev/bounties/1fa1aac9-b16a-4a70-a7da-960b3908ae1d
