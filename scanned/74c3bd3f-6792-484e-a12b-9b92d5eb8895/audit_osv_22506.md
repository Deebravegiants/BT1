# [H] SQL injection via the field name of a tracker in Tuleap

## Summary
Severity: High
Advisory: CVE-2022-31058
Aliases: GHSA-4v2p-rwq9-3vjf
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-29
Source: https://osv.dev/vulnerability/CVE-2022-31058
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. In versions prior to 13.9.99.95 Tuleap does not sanitize properly user inputs when constructing the SQL query to retrieve data for the tracker reports. An attacker with the capability to create a new tracker can execute arbitrary SQL queries. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31058.json
- https://github.com/Enalean/tuleap/commit/b91bcd57c8344ec2a4c1833629e400cef4dd901a
- https://github.com/Enalean/tuleap/security/advisories/GHSA-4v2p-rwq9-3vjf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31058
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=b91bcd57c8344ec2a4c1833629e400cef4dd901a
- https://tuleap.net/plugins/tracker/?aid=27172
