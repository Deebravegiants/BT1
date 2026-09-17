# [H] Activepieces: Arbitrary file write in git-sync via path traversal and symlinks

## Summary
Severity: High
Advisory: CVE-2026-53535
Aliases: GHSA-qqcr-rg2x-97mm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-53535
Type: osv

## Details
Activepieces is an open source AI workflow automation platform. Prior to 0.82.0, the git-sync feature clones a user-configured Git repository into a temporary directory on the server and then writes flow, table, and connection state into it before pushing back, and two separate weaknesses allowed those writes to escape the intended workspace and land on arbitrary paths on the host filesystem: Git's symbolic-link handling was not disabled on the clone, so an attacker who controlled the remote repository could include symlinks that redirected the writes, and several user-supplied identifiers used to build on-disk paths (the repository slug and the externalId of tables, flows, and connections) were not validated against directory-traversal sequences such as ../. On a self-hosted Enterprise Edition deployment, a user authorized to configure or push to a git-sync repository (holding the WRITE_PROJECT_RELEASE permission) could cause the server to overwrite files anywhere the Activepieces process user can write, which depending on host layout can be leveraged for tampering, denial of service, or remote code execution. This issue is fixed in version 0.82.0.

## References
- https://github.com/activepieces/activepieces/releases/tag/0.82.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53535.json
- https://github.com/activepieces/activepieces/security/advisories/GHSA-qqcr-rg2x-97mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53535
- https://github.com/activepieces/activepieces/commit/01bd4ef76fc1ad1bf7adc10c39ece4f624da6bf5
- https://github.com/activepieces/activepieces/pull/12711
