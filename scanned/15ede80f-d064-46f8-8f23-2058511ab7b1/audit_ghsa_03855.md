# [H] Path Traversal in LibreNMS

## Summary
Severity: High
Advisory: GHSA-r336-jxfr-4c3c
CVE: CVE-2019-12464
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-r336-jxfr-4c3c
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.53

## Details
An issue was discovered in LibreNMS 1.50.1. An authenticated user can perform a directory traversal attack against the /pdf.php file with a partial filename in the report parameter, to cause local file inclusion resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12464
- https://www.darkmatter.ae/xen1thlabs/librenms-limited-local-file-inclusion-via-directory-traversal-vulnerability-xl-19-019
