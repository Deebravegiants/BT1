# [M] Directory traversal in Nextcloud server

## Summary
Severity: Medium
Advisory: CVE-2023-25579
Aliases: GHSA-273v-9h7x-p68v
CVSS: 6.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-02-22
Source: https://osv.dev/vulnerability/CVE-2023-25579
Type: osv

## Details
Nextcloud server is a self hosted home cloud product. In affected versions the `OC\Files\Node\Folder::getFullPath()` function was validating and normalizing the string in the wrong order. The function is used in the `newFile()` and `newFolder()` items, which may allow to creation of paths outside of ones own space and overwriting data from other users with crafted paths. This issue has been addressed in versions 25.0.2, 24.0.8, and 23.0.12. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25579.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-273v-9h7x-p68v
- https://nvd.nist.gov/vuln/detail/CVE-2023-25579
- https://github.com/nextcloud/server/pull/35074
