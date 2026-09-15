# [M] Halloy has a file transfer path traveral vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-32733
Aliases: GHSA-fqrv-rfg4-rv89
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32733
Type: osv

## Details
Halloy is an IRC application written in Rust. Prior to commit 0f77b2cfc5f822517a256ea5a4b94bad8bfe38b6, the DCC receive flow did not sanitize filenames from incoming `DCC SEND` requests. A remote IRC user could send a filename with path traversal sequences like `../../.ssh/authorized_keys` and the file would be written outside the user's configured `save_directory`. With auto-accept enabled this required zero interaction from the victim. Starting with commit 0f77b2cfc5f822517a256ea5a4b94bad8bfe38b6, all identified code paths sanitize filenames through a shared `sanitize_filename` function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32733.json
- https://github.com/squidowl/halloy/security/advisories/GHSA-fqrv-rfg4-rv89
- https://nvd.nist.gov/vuln/detail/CVE-2026-32733
- https://github.com/squidowl/halloy/commit/0f77b2cfc5f822517a256ea5a4b94bad8bfe38b6
