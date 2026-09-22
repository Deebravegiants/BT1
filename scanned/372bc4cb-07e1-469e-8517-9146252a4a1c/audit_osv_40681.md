# [H] Pi: Predictable temporary extension install paths allow local privilege escalation on shared Linux hosts

## Summary
Severity: High
Advisory: CVE-2026-54328
Aliases: GHSA-jfgx-wxx8-mp94
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-54328
Type: osv

## Details
Pi is a minimal terminal coding harness. From 0.74.0 until 0.78.1, Pi versions with temporary npm or git extension package installs used predictable paths under the operating system temporary directory. On Linux-based multi-user systems, a local attacker who can write to the shared temporary directory could prepare the expected package location before another user runs pi with a temporary extension package source. Pi could then load attacker-controlled extension code in the victim user's process.  This vulnerability is fixed in 0.78.1.

## References
- https://github.com/earendil-works/pi/releases/tag/v0.78.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54328.json
- https://github.com/earendil-works/pi/security/advisories/GHSA-jfgx-wxx8-mp94
- https://nvd.nist.gov/vuln/detail/CVE-2026-54328
- https://github.com/earendil-works/pi/commit/a98e087e5d08ea2a536bf73dbb0aebb87c3ef72e
- https://github.com/earendil-works/pi/commit/ea3465a8e371a12d0167a06b60f93878e3a3df44
- https://github.com/earendil-works/pi/pull/5345
