# [H] Ella Core has Privilege Escalation via Database Restore by NetworkManager role

## Summary
Severity: High
Advisory: GHSA-87j9-m7x6-hvw2
CVE: CVE-2026-33906
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-87j9-m7x6-hvw2
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.7.0

## Details
## Summary

The NetworkManager role was granted backup and restore permission. The restore endpoint accepted any valid SQLite file without verifying its contents.

## Impact

A NetworkManager could replace the production database with a tampered copy to escalate to Admin, gaining access to user management, audit logs, debug endpoints, and operator identity configuration that the role was explicitly denied.

## Fix 

Backup and restore permissions have been removed from the NetworkManager role.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-87j9-m7x6-hvw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33906
- https://github.com/ellanetworks/core/commit/1e4768288a6519fcb63ec83f851584ecebb8a972
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.7.0
