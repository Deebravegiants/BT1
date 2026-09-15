# [M] go-git improperly verifies data integrity values for .idx and .pack files

## Summary
Severity: Medium
Advisory: GHSA-37cx-329c-33x3
CVE: CVE-2026-25934
CWE: CWE-354
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-37cx-329c-33x3
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.16.5

## Details
### Impact 

A vulnerability was discovered in `go-git` whereby data integrity values for `.pack` and `.idx` files were not properly verified. This resulted in `go-git` potentially consuming corrupted files, which would likely result in unexpected errors such as `object not found`.

For context, clients fetch [`packfiles`](https://git-scm.com/docs/pack-protocol#_packfile_data) from upstream Git servers. Those files contain a checksum of their contents, so that clients can perform integrity checks before consuming it. The pack indexes (`.idx`) are [generated](https://git-scm.com/docs/pack-format) locally by `go-git`, or the `git` cli, when new `.pack` files are received and processed. The integrity checks for both files were not being verified correctly.

Note that the lack of verification of the packfile checksum has no impact on the trust relationship between the client and server, which is enforced based on the protocol being used (e.g. TLS in the case of `https://` or known hosts for `ssh://`). In other words, the packfile checksum verification does not provide any security benefits when connecting to a malicious or compromised Git server.

### Patches

Users should upgrade to `v5.16.5`, or the latest `v6` [pseudo-version](https://go.dev/ref/mod#pseudo-versions), in order to mitigate this vulnerability.

### Workarounds

In case updating to a fixed version of `go-git` is not possible, users can run [git fsck](https://git-scm.com/docs/git-fsck) from the `git` cli to check for data corruption on a given repository. 

### Credit

Thanks @N0zoM1z0 for finding and reporting this issue privately to the `go-git` project.

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-37cx-329c-33x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25934
- https://github.com/go-git/go-git
- https://github.com/go-git/go-git/releases/tag/v5.16.5
