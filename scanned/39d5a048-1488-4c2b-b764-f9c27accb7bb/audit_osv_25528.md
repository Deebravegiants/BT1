# [M] Tuleap allows preview of a linked artifact with a type does not respect permissions

## Summary
Severity: Medium
Advisory: CVE-2023-38508
Aliases: GHSA-h637-g4xp-2992
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-24
Source: https://osv.dev/vulnerability/CVE-2023-38508
Type: osv

## Details
Tuleap is an open source suite to improve management of software developments and collaboration. In Tuleap Community Edition prior to version 14.11.99.28 and Tuleap Enterprise Edition prior to versions 14.10-6 and 14.11-3, the preview of an artifact link with a type does not respect the project, tracker and artifact level permissions. The issue occurs on the artifact view (not reproducible on the artifact modal). Users might get access to information they should not have access to. Only the title, status, assigned to and last update date fields as defined by the semantics are impacted. If those fields have strict permissions (e.g. the title is only visible to a specific user group) those permissions are still enforced. Tuleap Community Edition 14.11.99.28, Tuleap Enterprise Edition 14.10-6, and Tuleap Enterprise Edition 14.11-3 contain a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38508.json
- https://github.com/Enalean/tuleap/commit/307c1c8044522a2dcc711062b18a3b3f9059a6c3
- https://github.com/Enalean/tuleap/security/advisories/GHSA-h637-g4xp-2992
- https://nvd.nist.gov/vuln/detail/CVE-2023-38508
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=307c1c8044522a2dcc711062b18a3b3f9059a6c3
- https://tuleap.net/plugins/tracker/?aid=33608
