# [H] TeamPass files are available without authentication

## Summary
Severity: High
Advisory: GHSA-83h6-22cp-f22w
CVE: CVE-2020-12478
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-83h6-22cp-f22w
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected 2.1.27.36

## Details
TeamPass 2.1.27.36 allows an unauthenticated attacker to retrieve files from the TeamPass web root. This may include backups or LDAP debug files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12478
- https://github.com/nilsteampassnet/TeamPass/issues/2764
- https://github.com/nilsteampassnet/TeamPass
