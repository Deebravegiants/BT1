# [H] Go-Ethereum vulnerable to denial of service via malicious p2p message

## Summary
Severity: High
Advisory: GHSA-ppjg-v974-84cm
CVE: CVE-2023-40591
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-ppjg-v974-84cm
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.12.1-stable

## Details
### Impact

A vulnerable node, can be made to consume unbounded amounts of memory when handling specially crafted p2p messages sent from an attacker node.

### Details

The p2p handler spawned a new goroutine to respond to `ping` requests. By flooding a node with ping requests, an unbounded number of goroutines can be created, leading to resource exhaustion and potentially crash due to OOM.

### Patches

The fix is included in geth version `1.12.1-stable`, i.e, `1.12.2-unstable` and onwards. 

Fixed by https://github.com/ethereum/go-ethereum/pull/27887

### Workarounds

No known workarounds. 

### Credits

This bug was reported by Patrick McHardy and reported via [bounty@ethereum.org](mailto:bounty@ethereum.org). 

### References

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-ppjg-v974-84cm
- https://nvd.nist.gov/vuln/detail/CVE-2023-40591
- https://geth.ethereum.org/docs/developers/geth-developer/disclosures
- https://github.com/ethereum/go-ethereum
- https://github.com/ethereum/go-ethereum/releases/tag/v1.12.1
