# [C] MyBB: Installer database configuration RCE

## Summary
Severity: Critical
Advisory: CVE-2026-45117
Aliases: GHSA-gpc4-77rp-3xqr
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45117
Type: osv

## Details
MyBB is free and open source forum software. From 1.8.13 until 1.8.40, the installer module does not properly escape user-supplied database configuration values written to the configuration file, resulting in PHP code injection and remote code execution when the installer is available. install/index.php processes the values with addcslashes(), but the $characters argument added in MyBB 1.8.13 does not include the backslash character, allowing crafted input to escape the generated PHP string. The uniquely identifying implementation details include introduced in MyBB 1.8.13. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45117.json
- https://github.com/mybb/mybb/security/advisories/GHSA-gpc4-77rp-3xqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45117
- https://github.com/mybb/mybb/commit/0fe713e3b964bfc878ea65bdd9f746f585f6ebbf
