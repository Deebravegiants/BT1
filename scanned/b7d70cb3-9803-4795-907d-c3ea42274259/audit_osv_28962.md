# [C] Open eClass Platform allows Arbitrary File Upload in "modules/h5p/save.php"

## Summary
Severity: Critical
Advisory: CVE-2024-38530
Aliases: GHSA-88c3-hp7p-grgg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-38530
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete Course Management System. An arbitrary file upload vulnerability in the "save" functionality of the H5P module enables unauthenticated users to upload arbitrary files on the server's filesystem. This may lead in unrestricted RCE on the backend server, since the upload location is accessible from the internet. This vulnerability is fixed in 3.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38530.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-88c3-hp7p-grgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-38530
- https://github.com/gunet/openeclass/commit/4449cf8bed40fd8fc4b267a5726fab9f9fe5a191
