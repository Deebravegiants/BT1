# [M] Resources of private projects can be exposed in Tuleap

## Summary
Severity: Medium
Advisory: CVE-2022-31032
Aliases: GHSA-hvx6-4228-whj3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-29
Source: https://osv.dev/vulnerability/CVE-2022-31032
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. In versions prior to 13.9.99.58 authorizations are not properly verified when creating projects or trackers from projects marked as templates. Users can get access to information in those template projects because the permissions model is not properly enforced. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://docs.tuleap.org/administration-guide/users-management/security/site-access.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31032.json
- https://github.com/Enalean/tuleap/commit/7e221a9d1893c13407b35008762757a76d8e5654
- https://github.com/Enalean/tuleap/commit/cc38bcc59ce0c733ca915d95daec5f3082fb17ca
- https://github.com/Enalean/tuleap/security/advisories/GHSA-hvx6-4228-whj3
- https://nvd.nist.gov/vuln/detail/CVE-2022-31032
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=7e221a9d1893c13407b35008762757a76d8e5654
- https://tuleap.net/plugins/tracker/?aid=26816
