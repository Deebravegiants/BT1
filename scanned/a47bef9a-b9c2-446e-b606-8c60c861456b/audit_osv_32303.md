# [M] In Tuleap, deleting a report can delete criteria filters in other reports

## Summary
Severity: Medium
Advisory: CVE-2025-27401
Aliases: GHSA-3rjf-87rf-h8m9
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-27401
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. In a standard usages of Tuleap, the issue has a limited impact, it will mostly leave dangling data. However, a malicious user could create and delete reports multiple times to cycle through all the filters of all reports of the instance and delete them. The malicious user only needs to have access to one tracker. This would result in the loss of all criteria filters forcing users and tracker admins to re-create them. This vulnerability is fixed in Tuleap Community Edition 16.4.99.1740498975 and Tuleap Enterprise Edition 16.4-6 and 16.3-11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27401.json
- https://github.com/Enalean/tuleap/commit/0070fef5c3b27fd402d3232041c6e03f79a84ffd
- https://github.com/Enalean/tuleap/security/advisories/GHSA-3rjf-87rf-h8m9
- https://nvd.nist.gov/vuln/detail/CVE-2025-27401
- https://tuleap.net/plugins/tracker/?aid=41850
