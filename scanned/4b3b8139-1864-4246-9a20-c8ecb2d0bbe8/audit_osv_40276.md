# [H] Streambert: Arbitrary Directory Creation and File Manipulation via Backup Handler

## Summary
Severity: High
Advisory: CVE-2026-52875
Aliases: GHSA-c64m-cx97-6rc9
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-52875
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Prior to 2.6.0, the perform-scheduled-backup IPC handler in src/ipc/storage.js takes settings.path from a renderer-supplied object and uses the resulting directory for fs.mkdirSync, fs.writeFileSync, fs.readdirSync, and fs.unlinkSync operations without checking that it is inside an authorized backup location. A compromised renderer can choose an absolute path or a relative traversal path to create directories and write a streambert-backup-[timestamp].json file containing renderer-controlled data. The pruning loop can also delete files in that directory whose names begin with streambert-backup- and end with .json. This vulnerability is fixed in 2.6.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52875.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-c64m-cx97-6rc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-52875
- http://github.com/truelockmc/streambert/commit/43566ed031183b046675761c9813c5379b619269
- https://github.com/truelockmc/streambert/pull/149
