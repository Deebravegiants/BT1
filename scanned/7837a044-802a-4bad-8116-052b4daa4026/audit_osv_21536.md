# [H] CVE-2021-43806

## Summary
Severity: High
Advisory: CVE-2021-43806
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-43806
Type: osv

## Details
Tuleap is a Libre and Open Source tool for end to end traceability of application and system developments. In affected versions Tuleap does not sanitize properly user settings when constructing the SQL query to browse and search commits in the CVS repositories. A authenticated malicious user with read access to a CVS repository could execute arbitrary SQL queries. Tuleap instances without an active CVS repositories are not impacted. The following versions contain the fix: Tuleap Community Edition 13.2.99.155, Tuleap Enterprise Edition 13.1-7, and Tuleap Enterprise Edition 13.2-6.

## References
- https://github.com/Enalean/tuleap/commit/b82be896b00a787ed46a77bd4700e8fccfe2e5ba
- https://github.com/Enalean/tuleap/security/advisories/GHSA-x8fr-8gvw-cc4v
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=b82be896b00a787ed46a77bd4700e8fccfe2e5ba
- https://tuleap.net/plugins/tracker/?aid=24202
