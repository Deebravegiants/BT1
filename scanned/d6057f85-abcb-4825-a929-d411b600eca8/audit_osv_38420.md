# [C] Cacti: Unauthenticated RCE on Graph Image

## Summary
Severity: Critical
Advisory: CVE-2026-39938
Aliases: GHSA-rm7p-qcqm-x5m6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-39938
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior have unauthenticated LFI through graph_theme and rrdtool IPC serialization hardening. This issue has been resolved in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39938.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-rm7p-qcqm-x5m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-39938
- https://github.com/Cacti/cacti/commit/9871f0cef9af285398d558c9b3188d5977e01a04
