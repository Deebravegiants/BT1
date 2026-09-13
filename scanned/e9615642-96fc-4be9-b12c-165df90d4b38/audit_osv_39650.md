# [M] osquery: Unprivileged users can temporarily read file carve contents

## Summary
Severity: Medium
Advisory: CVE-2026-46388
Aliases: GHSA-fg78-9q98-62hh
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-46388
Type: osv

## Details
osquery is a SQL powered operating system instrumentation, monitoring, and analytics framework. Prior to 5.23.1, an unprivileged attacker can read the contents of an osquery file carve until the carve completes and the temporary files are deleted because in-progress carve directories are not created with private permissions. If the carve targets a directory that the attacker controls, arbitrary file reads are possible, such as sensitive local files. This issue is fixed in version 5.23.1.

## References
- https://github.com/osquery/osquery/releases/tag/5.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46388.json
- https://github.com/osquery/osquery/security/advisories/GHSA-fg78-9q98-62hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46388
- https://github.com/osquery/osquery/commit/6dabe9ded33bf9c6fc0f3e37ec364a1cbbd25d68
- https://github.com/osquery/osquery/pull/8961
