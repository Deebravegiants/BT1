# [M] Ghost has SQL Injection in Members Activity Feed

## Summary
Severity: Medium
Advisory: GHSA-gjrp-xgmh-x9qq
CVE: CVE-2026-22596
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-gjrp-xgmh-x9qq
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.0 <6.11.0
- npm: `ghost` — affected >=5.105.0 <5.130.6

## Details
### Impact
A vulnerability in Ghost's `/ghost/api/admin/members/events` endpoint allows users with authentication credentials for the Admin API to execute arbitrary SQL.

### Vulnerable versions
This vulnerability is present in Ghost v5.90.0 to v5.130.5 to and Ghost v6.0.0 to v6.10.3.

### Patches
v5.130.6 and v6.11.0 contain a fix for this issue.

### References
Ghost thanks Sho Odagiri of GMO Cybersecurity by Ierae, Inc. for discovering and disclosing this vulnerability responsibly.

### For more information
If there are any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-gjrp-xgmh-x9qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-22596
- https://github.com/TryGhost/Ghost/commit/cda236e455a7a30e828b6cba3c430e5796ded955
- https://github.com/TryGhost/Ghost/commit/f2165f968bcdaae0e35590b38fa280ab03239391
- https://github.com/TryGhost/Ghost
