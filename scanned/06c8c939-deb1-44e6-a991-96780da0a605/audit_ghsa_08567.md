# [M] go-billy: Lack of depth and cycle detection in symlink resolution may lead to infinite loops and resource exhaustion

## Summary
Severity: Medium
Advisory: GHSA-m3xc-h892-ggx6
CVE: CVE-2026-44740
CWE: CWE-674, CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-m3xc-h892-ggx6
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-billy/v5` — affected >=0 <5.9.0
- Go: `github.com/go-git/go-billy/v6` — affected >=0 <6.0.0-alpha.1

## Details
### Impact
Multiple components may improperly handle crafted or malformed input, resulting in panics, infinite loops, uncontrolled recursion, or excessive resource consumption.

These issues arise from insufficient validation and missing safety mechanisms such as cycle detection, recursion limits, or defensive handling of unexpected states when processing untrusted repository data and filesystem structures.

### Patches
Users should upgrade to a patched version in order to mitigate this vulnerability. Versions prior to `v5` are likely to be affected, users are recommended to upgrade to a supported `go-billy` version.

### Credits
Thanks to @faran66 for finding and reporting this issue privately to the go-git project. 🙇

## References
- https://github.com/go-git/go-billy/security/advisories/GHSA-m3xc-h892-ggx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44740
- https://github.com/go-git/go-billy
- https://github.com/go-git/go-billy/releases/tag/v5.9.0
- https://github.com/go-git/go-billy/releases/tag/v6.0.0-alpha.1
