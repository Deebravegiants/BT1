# [H] CoreDNS vulnerable to TuDoor Attacks

## Summary
Severity: High
Advisory: GHSA-hfmw-7g3m-gj6q
CVE: CVE-2023-28452
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-hfmw-7g3m-gj6q
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.11.0

## Details
An issue was discovered in CoreDNS through 1.10.1. There is a vulnerability in DNS resolving software, which triggers a resolver to ignore valid responses, thus causing denial of service for normal resolution. In an exploit, the attacker could just forge a response targeting the source port of a vulnerable resolver without the need to guess the correct TXID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28452
- https://github.com/coredns/coredns/commit/604a902e2c7e0317aecaa3666124079c75a31573
- https://coredns.io
- https://gist.github.com/idealeer/e41c7fb3b661d4262d0b6f21e12168ba
- https://github.com/advisories/GHSA-hfmw-7g3m-gj6q
- https://github.com/coredns/coredns
