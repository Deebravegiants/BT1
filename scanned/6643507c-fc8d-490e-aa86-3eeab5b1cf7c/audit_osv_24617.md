# [M] ownCloud Android app vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2023-23948
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/CVE-2023-23948
Type: osv

## Details
The ownCloud Android app allows ownCloud users to access, share, and edit files and folders. Version 2.21.1 of the ownCloud Android app is vulnerable to SQL injection in `FileContentProvider.kt`. This issue can lead to information disclosure. Two databases, `filelist` and `owncloud_database`, are affected. In version 3.0, the `filelist` database was deprecated. However, injections affecting `owncloud_database` remain relevant as of version 3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23948.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23948
- https://securitylab.github.com/advisories/GHSL-2022-059_GHSL-2022-060_Owncloud_Android_app/
