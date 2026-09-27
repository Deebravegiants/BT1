# [C] Arbitrary file reading vulnerability in Aim

## Summary
Severity: Critical
Advisory: GHSA-8phj-f9w2-cjcc
CVE: CVE-2021-43775
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-8phj-f9w2-cjcc
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0 <3.1.0

## Details
### Impact
A path traversal attack aims to access files and directories that are stored outside the web root folder. By manipulating variables that reference files with “dot-dot-slash (../)” sequences and its variations or by using absolute file paths, it may be possible to access arbitrary files and directories stored on file system including application source code or configuration and critical system files.

Vulnerable code: https://github.com/aimhubio/aim/blob/0b99c6ca08e0ba7e7011453a2f68033e9b1d1bce/aim/web/api/views.py#L9-L16

### Patches
The vulnerability issue is resolved in Aim v3.1.0.

### References
https://owasp.org/www-community/attacks/Path_Traversal

## References
- https://github.com/aimhubio/aim/security/advisories/GHSA-8phj-f9w2-cjcc
- https://nvd.nist.gov/vuln/detail/CVE-2021-43775
- https://github.com/aimhubio/aim/issues/999
- https://github.com/aimhubio/aim/pull/1003
- https://github.com/aimhubio/aim/commit/b9e53df5e32d14bbd3a2c738e2db7187fb531e93
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/0b99c6ca08e0ba7e7011453a2f68033e9b1d1bce/aim/web/api/views.py#L9-L16
- https://github.com/pypa/advisory-database/tree/main/vulns/aim/PYSEC-2021-839.yaml
