# [H] Gogs Directory Traversal

## Summary
Severity: High
Advisory: GHSA-9hxg-w7qf-hh93
CVE: CVE-2018-20303
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9hxg-w7qf-hh93
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.11.80-0.20181218063808-ff93d9dbda5c

## Details
In pkg/tool/path.go in Gogs before 0.11.82.1218, a directory traversal in the file-upload functionality can allow an attacker to create a file under data/sessions on the server, a similar issue to CVE-2018-18925.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20303
- https://github.com/gogs/gogs/issues/5558
- https://github.com/gogs/gogs/commit/ff93d9dbda5cebe90d86e4b7dfb2c6b8642970ce
- https://github.com/gogs/gogs
- https://pentesterlab.com/exercises/cve-2018-18925
