# [H] CVE-2021-41148

## Summary
Severity: High
Advisory: CVE-2021-41148
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-15
Source: https://osv.dev/vulnerability/CVE-2021-41148
Type: osv

## Details
Tuleap Open ALM is a libre and open source tool for end to end traceability of application and system developments. Prior to version 11.16.99.173 of Community Edition and versions 11.16-6 and 11.15-8 of Enterprise Edition, an attacker with the ability to add one the CI widget to its personal dashboard could execute arbitrary SQL queries. Tuleap Community Edition 11.16.99.173, Tuleap Enterprise Edition 11.16-6, and Tuleap Enterprise Edition 11.15-8 contain a patch for this issue.

## References
- https://tuleap.net/plugins/tracker/?aid=15028
- https://github.com/Enalean/tuleap/commit/91535add59f4b3a04b6b8eab123c002cd5af180d
- https://github.com/Enalean/tuleap/security/advisories/GHSA-3c4q-8c35-cp63
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=91535add59f4b3a04b6b8eab123c002cd5af180d
