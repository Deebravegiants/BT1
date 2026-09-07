# [H] go-ethereum is vulnerable to high CPU usage leading to DoS via malicious p2p message

## Summary
Severity: High
Advisory: GHSA-mq3p-rrmp-79jg
CVE: CVE-2026-22868
CWE: CWE-20, CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-mq3p-rrmp-79jg
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.16.8

## Details
**Impact**

An attacker can cause high CPU usage by sending a specially crafted p2p message.
More details to be released later.

**Credit**

This issue was reported to the Ethereum Foundation Bug Bounty Program by @Yenya030

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-mq3p-rrmp-79jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-22868
- https://github.com/ethereum/go-ethereum/commit/abeb78c647e354ed922726a1d719ac7bc64a07e2
- https://github.com/ethereum/go-ethereum
