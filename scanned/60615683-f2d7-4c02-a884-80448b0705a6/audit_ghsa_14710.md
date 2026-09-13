# [M] TeamPass mail_me operation authorization issue

## Summary
Severity: Medium
Advisory: GHSA-7rm3-4w6j-8xx4
CVE: CVE-2024-50702
CWE: CWE-266, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-30
Source: https://github.com/advisories/GHSA-7rm3-4w6j-8xx4
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.1.3.1

## Details
TeamPass before 3.1.3.1 does not properly check whether a mail_me (aka action_mail) operation is on behalf of an administrator or manager.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50702
- https://github.com/nilsteampassnet/TeamPass/commit/35e2b479f2379545b4132bc30a9d052ba7018bf9
- https://github.com/nilsteampassnet/TeamPass
- https://github.com/nilsteampassnet/TeamPass/compare/3.1.2...3.1.3.1
- https://github.com/nilsteampassnet/TeamPass/compare/3.1.3...3.1.3.1
