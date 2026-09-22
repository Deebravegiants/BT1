# [H] elFinder vulnerable to path traversal in LocalVolumeDriver connector

## Summary
Severity: High
Advisory: GHSA-wm5g-p99q-66g4
CVE: CVE-2023-35840
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-wm5g-p99q-66g4
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.62

## Details
### Impact
Path Traversal vulnerability in PHP LocalVolumeDriver connector. This vulnerability can be exploited by allowing untrusted users to write to the local file system.

This issue was caused by incomplete validity checking of the supplied request parameters. That problem has been fixed in elFinder Version 2.1.62.

### Patches
This vulnerability has been fixed in elFinder 2.1.62. Installation managers should update to the latest version as soon as possible.

### Workarounds
If you cannot update for some reason, you must stop using it or prohibit writing to untrusted users.

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-wm5g-p99q-66g4
- https://github.com/Studio-42/elFinder/commit/bb9aaa7b096a1b83f2f85657c43f12131ece2891
- https://github.com/Studio-42/elFinder
