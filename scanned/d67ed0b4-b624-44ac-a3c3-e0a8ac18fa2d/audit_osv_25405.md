# [M] User access not updated with privilege change in Tuleap

## Summary
Severity: Medium
Advisory: CVE-2023-35938
Aliases: GHSA-rq42-cv6q-3m9q
CVSS: 4.1 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-06-29
Source: https://osv.dev/vulnerability/CVE-2023-35938
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. When switching from a project visibility that allows restricted users to `Private without restricted`, restricted users that are project administrators keep this access right. Restricted users that were project administrators before the visibility switch keep the possibility to access the project and do some administration actions. This issue has been resolved in Tuleap version 14.9.99.63. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35938.json
- https://github.com/Enalean/tuleap/commit/a108186e7538676c4bf6e615f793f3b787a09b91
- https://github.com/Enalean/tuleap/security/advisories/GHSA-rq42-cv6q-3m9q
- https://nvd.nist.gov/vuln/detail/CVE-2023-35938
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=a108186e7538676c4bf6e615f793f3b787a09b91
- https://tuleap.net/plugins/tracker/?aid=32278
