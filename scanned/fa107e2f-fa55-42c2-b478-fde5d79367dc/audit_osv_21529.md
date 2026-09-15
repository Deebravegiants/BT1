# [H] CVE-2021-43782

## Summary
Severity: High
Advisory: CVE-2021-43782
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-43782
Type: osv

## Details
Tuleap is a Libre and Open Source tool for end to end traceability of application and system developments. This is a follow up to GHSA-887w-pv2r-x8pm/CVE-2021-41276, the initial fix was incomplete. Tuleap does not sanitize properly the search filter built from the ldap_id attribute of a user during the daily synchronization. A malicious user could force accounts to be suspended or take over another account by forcing the update of the ldap_uid attribute. Note that the malicious user either need to have site administrator capability on the Tuleap instance or be an LDAP operator with the capability to create/modify account. The Tuleap instance needs to have the LDAP plugin activated and enabled for this issue to be exploitable. The following versions contain the fix: Tuleap Community Edition 13.2.99.83, Tuleap Enterprise Edition 13.1-6, and Tuleap Enterprise Edition 13.2-4.

## References
- https://github.com/Enalean/tuleap/security/advisories/GHSA-887w-pv2r-x8pm
- https://github.com/Enalean/tuleap/security/advisories/GHSA-cwv9-hhm4-jr84
- https://github.com/Enalean/tuleap/commit/64e77561eba9f8233199c2962b3497ed7294a7d2
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=64e77561eba9f8233199c2962b3497ed7294a7d2
- https://tuleap.net/plugins/tracker/?aid=24168
