# [H] Dosage vulnerable to a Directory Traversal through crafted HTTP responses

## Summary
Severity: High
Advisory: GHSA-4vcx-3pj3-44m7
CVE: CVE-2025-64184
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-04
Source: https://github.com/advisories/GHSA-4vcx-3pj3-44m7
Type: github-advisory

## Affected
- PyPI: `dosage` — affected >=0 <3.2

## Details
### Impact

When downloadinging comic images, Dosage constructs target file names from different aspects of the remote comic (page URL, image URL, page content, etc.). While the basename is properly stripped of directory-traversing characters, the file extension is taken from the HTTP `Content-Type` header. This allows a remote attacker (or a Man-in-the-Middle, if the comic is served over HTTP) to write arbitrary files outside the target directory (if additional conditions are met). 

### Patches

Fixed in release 3.2. The [fix is small and self-contained](https://github.com/webcomics/dosage/commit/336a9684191604bc49eed7296b74bd582151181e), so distributors might elect to backport the fix to older versions.

### Workarounds

No

## References
- https://github.com/webcomics/dosage/security/advisories/GHSA-4vcx-3pj3-44m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-64184
- https://github.com/webcomics/dosage/commit/336a9684191604bc49eed7296b74bd582151181e
- https://github.com/webcomics/dosage
