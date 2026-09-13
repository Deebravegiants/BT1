# [M] go-git: Malformed Git object data may cause panics or resource exhaustion

## Summary
Severity: Medium
Advisory: GHSA-w5pp-99ch-qj29
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-w5pp-99ch-qj29
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.19.1
- Go: `github.com/go-git/go-git/v6` — affected >=0 <6.0.0-alpha.4

## Details
### Impact
Several denial-of-service issues were identified in `go-git` when parsing maliciously crafted Git repository data.

An attacker may craft a malicious `.pack`, `.idx` or loose objects that causes an application using an affected version of `go-git` to panic or consume excessive resources.

This can lead to denial of service in applications that use `go-git` to clone, fetch, open, or otherwise process untrusted repositories or Git object data.

Exploitation requires the ability to alter read-only files such as `.pack` or `.idx` from the local repository's `.git/objects/pack/` directory. Alternatively, the user would need to be interacting with a malicious remote server, which is not recommended and exposes users to a broader class of security risks beyond this issue.

### Patches
Users should upgrade to a patched version in order to mitigate this vulnerability. Versions prior to `v5` are likely to be affected, users are recommended to upgrade to a supported `go-git` version.

### Credits
go-git thanks @kodareef5, @AyushParkara and @N0zoM1z0 for reporting this in four separate reports. 🙇

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-w5pp-99ch-qj29
- https://github.com/go-git/go-git
