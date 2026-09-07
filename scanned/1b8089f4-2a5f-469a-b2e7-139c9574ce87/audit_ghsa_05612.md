# [H] go-ethereum is vulnerable to DoS via malicious p2p message affecting a vulnerable node

## Summary
Severity: High
Advisory: GHSA-mr7q-c9w9-wh4h
CVE: CVE-2026-22862
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-mr7q-c9w9-wh4h
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.16.8

## Details
**Impact**

A vulnerable node can be forced to shutdown/crash using a specially crafted message. 
More details to be released later.

**Credit**

This issue was reported to the Ethereum Foundation Bug Bounty Program by DELENE TCHIO ROMUALD.

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-mr7q-c9w9-wh4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-22862
- https://github.com/ethereum/go-ethereum/commit/abeb78c647e354ed922726a1d719ac7bc64a07e2
- https://github.com/ethereum/go-ethereum
