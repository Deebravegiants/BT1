# [M] CVE-2026-39245

## Summary
Severity: Medium
Advisory: CVE-2026-39245
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-39245
Type: osv

## Details
decompress before 4.2.2 contains an improper path containment check that enables directory traversal and arbitrary file write. The safeMakeDir function (index.js line 29) and the extraction path validation (index.js line 106) use String.indexOf() to verify the resolved path is within the output directory: realDestinationDir.indexOf(realOutputPath) !== 0. This check is flawed because it does not enforce a path separator boundary. For example, "/tmp/app_config".indexOf("/tmp/app") returns 0, incorrectly passing the check even though /tmp/app_config is outside /tmp/app. Combined with the unvalidated symlink creation in the same package, an attacker can write arbitrary files to directories adjacent to the extraction target. This is a bypass of the fix for CVE-2020-12265. The correct check requires appending a path separator: realParentPath.indexOf(realOutputPath + path.sep) !== 0.

## References
- https://www.npmjs.com/package/decompress
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39245.json
- https://nvd.nist.gov/vuln/detail/CVE-2020-12265
- https://nvd.nist.gov/vuln/detail/CVE-2026-39245
- https://github.com/kevva/decompress/issues/115
- https://github.com/kevva/decompress
