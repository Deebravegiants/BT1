# [H] path traversal via `config` parameter in qSnapper

## Summary
Severity: High
Advisory: CVE-2026-41046
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-41046
Type: osv

## Details
A path traversal attack when using a "configName" parameter in qSnapper before version 1.3.3 allowed a local attacker to use malicious config files for snapper and so cause a denial of service or potentially escalate privileges to root.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41046.json
- https://github.com/presire/qSnapper/releases/tag/v1.3.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41046
- https://security.opensuse.org/2026/05/26/qsnapper-dbus-issues.html#issue-path-traversal
- https://bugzilla.suse.com/show_bug.cgi?id=1261889
- https://github.com/presire/qSnapper
