# [M] CoreDNS Cache Poisoning via a birthday attack

## Summary
Severity: Medium
Advisory: GHSA-h92q-fgpp-qhrq
CVE: CVE-2023-30464
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-h92q-fgpp-qhrq
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0

## Details
CoreDNS through 1.10.1 enables attackers to achieve DNS cache poisoning and inject fake responses via a birthday attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30464
- https://github.com/coredns/coredns/commit/604a902e2c7e0317aecaa3666124079c75a31573
- https://gist.github.com/idealeer/e41c7fb3b661d4262d0b6f21e12168ba
- https://github.com/coredns/coredns
