# [M] rardecode: DoS risk due to unrestricted RAR dictionary sizes

## Summary
Severity: Medium
Advisory: GHSA-rwvp-r38j-9rgg
CVE: CVE-2025-11579
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-rwvp-r38j-9rgg
Type: github-advisory

## Affected
- Go: `github.com/nwaples/rardecode/v2` — affected >=0 <2.2.0
- Go: `github.com/nwaples/rardecode` — affected >=0

## Details
rardecode versions <= 2.1.1 fail to restrict the dictionary size when reading large RAR dictionary sizes, which allows an attacker to provide a specially crafted RAR file and cause Denial of Service via an Out Of Memory Crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11579
- https://github.com/nwaples/rardecode/commit/52fb4e825c936636f251f7e7deded39ab11df9a9
- https://github.com/nwaples/rardecode
- https://pkg.go.dev/vuln/GO-2025-4020
