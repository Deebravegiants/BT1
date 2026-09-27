# [H] Tuleap deleting or moving an artifact can delete values from unrelated artifacts

## Summary
Severity: High
Advisory: CVE-2024-30246
Aliases: GHSA-jc7g-4pcv-8jcj
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-30246
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. A malicious user could exploit this issue on purpose to delete information on the instance or possibly gain access to restricted artifacts. It is however not possible to control exactly which information is deleted. Information from theDate, File, Float, Int, List, OpenList, Text, and Permissions on artifact (this one can lead to the disclosure of restricted information) fields can be impacted.  This vulnerability is fixed in Tuleap Community Edition version 15.7.99.6 and Tuleap Enterprise Edition 15.7-2, 15.6-5, 15.5-6, 15.4-8, 15.3-6, 15.2-5, 15.1-9, 15.0-9, and 14.12-6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30246.json
- https://github.com/Enalean/tuleap/commit/a0ba0ae82a29eb8bfacef286778e5e49954f5316
- https://github.com/Enalean/tuleap/security/advisories/GHSA-jc7g-4pcv-8jcj
- https://nvd.nist.gov/vuln/detail/CVE-2024-30246
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=a0ba0ae82a29eb8bfacef286778e5e49954f5316
- https://tuleap.net/plugins/tracker/?aid=37545
