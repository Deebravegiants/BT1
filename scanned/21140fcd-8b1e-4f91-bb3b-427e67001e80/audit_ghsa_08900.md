# [H] go-git's improper parsing of specially crafted objects may lead to inconsistent interpretation compared to upstream Git

## Summary
Severity: High
Advisory: GHSA-389r-gv7p-r3rp
CVE: CVE-2026-45022
CWE: CWE-180, CWE-345
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-389r-gv7p-r3rp
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v6` — affected >=6.0.0-alpha.1 <6.0.0-alpha.3
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.19.0

## Details
### Impact
`go-git` may parse malformed Git objects in a way that differs from upstream Git. When `commit` or `tag` objects contain ambiguous or malformed headers, `go-git`’s decoded representation may expose values differently from how Git itself would interpret or reject the same object.

Additionally, `go-git`’s commit signing and verification logic operates over commit data reconstructed from `go-git`’s parsed representation rather than the original raw object bytes. As a result, `go-git` may sign or verify a commit payload that is not byte-for-byte equivalent to the object stored in the repository.

This can cause a signature to appear valid for a commit whose displayed or effective metadata differs from the object that was intended to be signed.

### Patches
Users should upgrade to a patched version in order to mitigate this vulnerability. Versions prior to v5 are likely to be affected, users are recommended to upgrade to a supported `go-git` version.

### Credit

Thanks to @bugbunny-research (https://bugbunny.ai/) for reporting this to `sigstore/gitsign`, and to @wlynch, @patzielinski and @adityasaky for coordinating the disclosure with the `go-git` project. :bow: :1st_place_medal: 

Thanks to @wayphinder for reporting this to the `go-git` project. :bow:

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-389r-gv7p-r3rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45022
- https://github.com/go-git/go-git
