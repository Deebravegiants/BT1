# [M] Tuleap has improper permission handling in the REST endpoints and release notes display of the FRS plugin

## Summary
Severity: Medium
Advisory: CVE-2025-30209
Aliases: GHSA-hcp5-pmpm-mgwh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-30209
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. An attacker can access release notes content or information via the FRS REST endpoints it should not have access to. This vulnerability is fixed in Tuleap Community Edition 16.5.99.1742812323 and Tuleap Enterprise Edition 16.5-6 and 16.4-10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30209.json
- https://github.com/Enalean/tuleap/commit/34af2d5d10b0349967129f53427f495815e5bbcc
- https://github.com/Enalean/tuleap/security/advisories/GHSA-hcp5-pmpm-mgwh
- https://nvd.nist.gov/vuln/detail/CVE-2025-30209
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=34af2d5d10b0349967129f53427f495815e5bbcc
- https://tuleap.net/plugins/tracker/?aid=42251
