# [M] Tuleap subject to Missing Authorization allowing for branch prefix modification

## Summary
Severity: Medium
Advisory: CVE-2022-39233
Aliases: GHSA-3884-972x-3ccq
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-39233
Type: osv

## Details
Tuleap is a Free & Open Source Suite to improve management of software developments and collaboration. In versions 12.9.99.228 and above, prior to 14.0.99.24, authorizations are not properly verified when updating the branch prefix used by the GitLab repository integration. Authenticated users can change the branch prefix of any of the GitLab repository integration they can see vie the REST endpoint `PATCH /gitlab_repositories/{id}`. This action should be restricted to Git administrators. This issue is patched in Tuleap Community Edition 14.0.99.24 and Tuleap Enterprise Edition 14.0-3. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39233.json
- https://github.com/Enalean/tuleap/commit/a06cb42d55c840d61a484472ed6b169ab23853ac
- https://github.com/Enalean/tuleap/security/advisories/GHSA-3884-972x-3ccq
- https://nvd.nist.gov/vuln/detail/CVE-2022-39233
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=a06cb42d55c840d61a484472ed6b169ab23853ac
- https://tuleap.net/plugins/tracker/?aid=28848
