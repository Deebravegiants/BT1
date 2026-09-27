# [M] Maliciously crafted remote URLs could lead to credential leak in GitHub Desktop

## Summary
Severity: Medium
Advisory: CVE-2025-23040
Aliases: GHSA-36mm-rh9q-cpqq
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2025-23040
Type: osv

## Details
GitHub Desktop is an open-source Electron-based GitHub app designed for git development. An attacker convincing a user to clone a repository directly or through a submodule can allow the attacker access to the user's credentials through the use of maliciously crafted remote URL. GitHub Desktop relies on Git to perform all network related operations (such as cloning, fetching, and pushing). When a user attempts to clone a repository GitHub Desktop will invoke `git clone` and when Git encounters a remote which requires authentication it will request the credentials for that remote host from GitHub Desktop using the git-credential protocol. Using a maliciously crafted URL it's possible to cause the credential request coming from Git to be misinterpreted by Github Desktop such that it will send credentials for a different host than the host that Git is currently communicating with thereby allowing for secret exfiltration. GitHub username and OAuth token, or credentials for other Git remote hosts stored in GitHub Desktop could be improperly transmitted to an unrelated host. Users should update to GitHub Desktop 3.4.12 or greater which fixes this vulnerability. Users who suspect they may be affected should revoke any relevant credentials.

## References
- https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps
- https://git-scm.com/docs/git-credential
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23040.json
- https://github.com/desktop/desktop/security/advisories/GHSA-36mm-rh9q-cpqq
- https://nvd.nist.gov/vuln/detail/CVE-2025-23040
