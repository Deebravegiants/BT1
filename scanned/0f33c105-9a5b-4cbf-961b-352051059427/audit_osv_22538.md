# [M] Fine grained permissions are not checked in Tuleap

## Summary
Severity: Medium
Advisory: CVE-2022-31128
Aliases: GHSA-2p49-vgcx-5w79
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/CVE-2022-31128
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. In affected versions Tuleap does not properly verify permissions when creating branches with the REST API in Git repositories using the fine grained permissions. Users can create branches via the REST endpoint `POST git/:id/branches` regardless of the permissions set on the repository. This issue has been fixed in version 13.10.99.82 Tuleap Community Edition as well as in version 13.10-3 of Tuleap Enterprise Edition. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31128.json
- https://github.com/Enalean/tuleap/commit/58ecb1dee1c46075d3e089980301ebfbe0bafd33
- https://github.com/Enalean/tuleap/security/advisories/GHSA-2p49-vgcx-5w79
- https://nvd.nist.gov/vuln/detail/CVE-2022-31128
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=58ecb1dee1c46075d3e089980301ebfbe0bafd33
- https://tuleap.net/plugins/tracker/?aid=27538
