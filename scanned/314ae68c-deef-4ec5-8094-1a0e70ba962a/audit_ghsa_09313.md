# [M] go-git: Crafted repositories may modify main and submodule .git directories

## Summary
Severity: Medium
Advisory: GHSA-crhj-59gh-8x96
CVE: CVE-2026-45571
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-crhj-59gh-8x96
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.19.1
- Go: `github.com/go-git/go-git/v6` — affected >=0 <6.0.0-alpha.4
- Go: `github.com/go-git/go-git` — affected >=0

## Details
### Impact
A path validation issue in `go-git` could allow crafted repository data to affect files outside the intended checkout target, including the repository's `.git` directory.

These validations were introduced in upstream Git years ago, so the vulnerability arose from go-git drifting from those checks. Some attack vectors were platform-specific: certain payloads affected only Windows users, others affected only macOS users, and some applied across all supported platforms.

Using non-descendant `go-billy` filesystem instances, or different filesystem types, for the `Storer` and `Worktree` may provide some isolation against `.git` directory manipulation. For example, users that store the `.git` directory through `memfs` while using `osfs` for the worktree are not affected by this vulnerability in the main repository, because repository metadata is not materialized inside the worktree filesystem.

However, this isolation does not necessarily apply when the repository contains submodules, since submodule dotgit directories may still be represented or materialized within the worktree context.

It is important to note that exploitation requires a maliciously crafted repository payload. Users should always exercise caution when interacting with repositories or Git servers they do not trust.

### Patches
Users should upgrade to a patched version in order to mitigate this vulnerability. Versions prior to `v5` are likely to be affected, users are recommended to upgrade to a supported go-git version.

### Credits
Thanks to @kodareef5, @AyushParkara and @N0zoM1z0 for reporting this to the go-git project in three separate reports. 🙇

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-crhj-59gh-8x96
- https://nvd.nist.gov/vuln/detail/CVE-2026-45571
- https://github.com/go-git/go-git
