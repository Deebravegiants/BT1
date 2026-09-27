# [H] go-billy has path traversal vulnerabilities

## Summary
Severity: High
Advisory: GHSA-qw64-3x98-g7q2
CVE: CVE-2026-44973
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-qw64-3x98-g7q2
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-billy/v5` — affected >=0 <5.9.0
- Go: `github.com/go-git/go-billy/v6` — affected >=0 <6.0.0-alpha.1

## Details
### Impact
Multiple path traversal issues exist across different components of `go-billy`. Insufficient path sanitization and boundary enforcement may allow crafted paths (e.g., using `..`) to escape intended base directories.

While go-billy was not originally designed to provide a strong security boundary, some of these issues were inconsistent across some of the built-in implementations. This results in scenarios where applications relying on `go-billy` for some level of isolation may inadvertently expose access to unintended filesystem locations.

The `osfs.ChrootOS` implementation is notably affected by this vulnerability and is now deprecated in `v5`, removed at `v6`. Users are recommended to move on to `osfs.BoundOS` instead: `osfs.New(path, WithBoundOS())`.

Users requiring stronger security boundary enforcement are recommended to upgrade to `v6`, where the `osfs` implementation are backed by the [traversal-resistant](https://go.dev/blog/osroot) primitive [os.Root](https://pkg.go.dev/os#Root).

### Patches
Users should upgrade to a patched version in order to mitigate this vulnerability. Versions prior to `v5` are likely to be affected, users are recommended to upgrade to a supported `go-billy` version.

### Credits
Thanks to @faran66 and @vnykmshr for finding and separately reporting this issue privately to the go-git project. 🙇

## References
- https://github.com/go-git/go-billy/security/advisories/GHSA-qw64-3x98-g7q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44973
- https://github.com/go-git/go-billy
- https://github.com/go-git/go-billy/releases/tag/v5.9.0
- https://github.com/go-git/go-billy/releases/tag/v6.0.0-alpha.1
