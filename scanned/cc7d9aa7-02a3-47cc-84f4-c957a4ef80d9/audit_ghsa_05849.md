# [M] n8n-nodes-sqlite3 vulnerable to path traversal via user-controlled database file path (db_path parameter)

## Summary
Severity: Medium
Advisory: GHSA-q7m3-rhxg-7vxr
CVE: CVE-2026-54687
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-q7m3-rhxg-7vxr
Type: github-advisory

## Affected
- npm: `n8n-nodes-sqlite3` — affected >=0 <1.0.0

## Details
## Affected versions
< 1.0.0

## Patched version
1.0.0

## Description
In versions prior to 1.0.0, the SQLite node accepted the database file
path as a direct node parameter visible and editable in the workflow.
A workflow author who mapped untrusted user input to the db_path field
could allow an attacker to control which file was opened by SQLite,
potentially enabling path traversal to read or overwrite arbitrary
files accessible to the n8n process.

The vulnerability requires the workflow author to explicitly wire
untrusted input to the db_path parameter, so it does not affect
standalone deployments where only trusted users author workflows.
However, in multi-tenant or user-facing n8n deployments the risk
is elevated.

Fixed in v1.0.0 by moving the database path into a credential
(v2 node architecture), which is stored server-side and not
controllable by workflow input data.

## References
- Fix commit: 145a887
- Introduced credential-based path: v2 node

## Credits
dyingman1 (role: Reporter)

## References
- https://github.com/DangerBlack/n8n-node-sqlite3/security/advisories/GHSA-q7m3-rhxg-7vxr
- https://github.com/DangerBlack/n8n-node-sqlite3/pull/25
- https://github.com/DangerBlack/n8n-node-sqlite3/commit/145a8876ff12375813bdcd4ae4fe78f460c53a98
- https://github.com/DangerBlack/n8n-node-sqlite3
