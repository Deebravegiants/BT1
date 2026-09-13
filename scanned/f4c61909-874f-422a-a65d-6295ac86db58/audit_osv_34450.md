# [M] Coolify leaksensitive information `email_change_code` in `/api/v1/teams/{team_id | current}/members` API endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-59955
Aliases: GHSA-927g-56xp-6427
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-59955
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Coolify versions prior to and including v4.0.0-beta.420.8 have an information disclosure vulnerability in the `/api/v1/teams/{team_id}/members` and `/api/v1/teams/current/members` API endpoints allows authenticated team members to access a highly sensitive `email_change_code` from other users on the same team. This code is intended for a single-use email change verification and should be kept secret. Its exposure could enable a malicious actor to perform an unauthorized email address change on behalf of the victim. As of time of publication, no known patched versions exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59955.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-927g-56xp-6427
- https://nvd.nist.gov/vuln/detail/CVE-2025-59955
