# [M] Tuleap backlog item representations do not verify the permissions of the child trackers

## Summary
Severity: Medium
Advisory: CVE-2025-59040
Aliases: GHSA-67xc-39v9-pffg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2025-59040
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. Backlog item representations do not verify the permissions of the child trackers. Users might see tracker names they should not have access to. This vulnerability is fixed in Tuleap Community Edition 16.11.99.1757427600 and Tuleap Enterprise Edition 16.11-6 and 16.10-8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59040.json
- https://github.com/Enalean/tuleap/commit/92e4aa2d830a624a9183206c1c3558b90b8a5525
- https://github.com/Enalean/tuleap/security/advisories/GHSA-67xc-39v9-pffg
- https://nvd.nist.gov/vuln/detail/CVE-2025-59040
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=92e4aa2d830a624a9183206c1c3558b90b8a5525
- https://tuleap.net/plugins/tracker/?aid=44489
