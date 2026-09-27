# [H] Server-side request forgery in BookWyrm

## Summary
Severity: High
Advisory: CVE-2022-23644
Aliases: GHSA-5m7g-66h6-5cvq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2022-23644
Type: osv

## Details
BookWyrm is a decentralized social network for tracking reading habits and reviewing books. The functionality to load a cover via url is vulnerable to a server-side request forgery attack. Any BookWyrm instance running a version prior to v0.3.0 is susceptible to attack from a logged-in user. The problem has been patched and administrators should upgrade to version 0.3.0 As a workaround, BookWyrm instances can close registration and limit members to trusted individuals.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23644.json
- https://github.com/bookwyrm-social/bookwyrm/security/advisories/GHSA-5m7g-66h6-5cvq
- https://nvd.nist.gov/vuln/detail/CVE-2022-23644
