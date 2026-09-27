# [H] CVE-2021-41155

## Summary
Severity: High
Advisory: CVE-2021-41155
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-41155
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. In affected versions Tuleap does not sanitize properly user inputs when constructing the SQL query to browse and search revisions in the CVS repositories. The following versions contain the fix: Tuleap Community Edition 11.17.99.146, Tuleap Enterprise Edition 11.17-5, Tuleap Enterprise Edition 11.16-7.

## References
- https://tuleap.net/plugins/tracker/?aid=16214
- https://github.com/Enalean/tuleap/commit/ff75f2899c60a4546ee2d532e68a3febd07bdd14
- https://github.com/Enalean/tuleap/security/advisories/GHSA-f8jp-hx4q-wxvr
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=ff75f2899c60a4546ee2d532e68a3febd07bdd14
