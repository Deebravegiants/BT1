# [H] TeamPass PHP arbitrary file include vulnerability

## Summary
Severity: High
Advisory: GHSA-6jf9-8m34-96w5
CVE: CVE-2020-12479
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6jf9-8m34-96w5
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0

## Details
TeamPass 2.1.27.36 allows any authenticated TeamPass user to trigger a PHP file include vulnerability via a crafted HTTP request with sources/users.queries.php newValue directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12479
- https://github.com/nilsteampassnet/TeamPass/issues/2762
- https://github.com/nilsteampassnet/TeamPass/pull/2874
- https://github.com/nilsteampassnet/TeamPass
