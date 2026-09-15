# [M] Denial of Service in Go-Ethereum

## Summary
Severity: Medium
Advisory: GHSA-5m8f-chrv-7rw5
CVE: CVE-2021-43668
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-5m8f-chrv-7rw5
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0

## Details
Go-Ethereum 1.10.9 nodes crash (denial of service) after receiving a serial of messages and cannot be recovered. They will crash with "runtime error: invalid memory address or nil pointer dereference" and arise a SEGV signal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43668
- https://github.com/ethereum/go-ethereum/issues/23866
- https://github.com/syndtr/goleveldb/issues/373
- https://github.com/ethereum/go-ethereum
