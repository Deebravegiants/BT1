# [H] TeamPass information exposure vulnerability

## Summary
Severity: High
Advisory: GHSA-2rhg-hqq9-8xjh
CVE: CVE-2023-3553
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-08
Source: https://github.com/advisories/GHSA-2rhg-hqq9-8xjh
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.0.10

## Details
TeamPass prior to 3.0.10 allows unauthenticated actors to view application-specific and user data and files by viewing an endpoint directory listing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3553
- https://github.com/nilsteampassnet/teampass/commit/e9f90b746fdde135da3c7fbe4fa22fe2bd32e66b
- https://github.com/nilsteampassnet/teampass
- https://huntr.dev/bounties/857f002a-2794-4807-aa5d-2f340de01870
