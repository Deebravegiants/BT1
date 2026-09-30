# [M] DoS via malicious p2p message in Go Ethereum

## Summary
Severity: Medium
Advisory: GHSA-wjxw-gh3m-7pm5
Aliases: CVE-2022-29177, GO-2022-0456
Package: github.com/ethereum/go-ethereum
Published: 2022-05-24
Source: https://osv.dev/vulnerability/GHSA-wjxw-gh3m-7pm5
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.10.17

## Details
### Impact

A vulnerable node, if configured to use high verbosity logging, can be made to crash when handling specially crafted p2p messages sent from an attacker node. 

### Patches

The following PR addresses the problem: https://github.com/ethereum/go-ethereum/pull/24507

### Workarounds

Aside from applying the PR linked above, setting loglevel to default level (`INFO`) makes the node not vulnerable to this attack.

### Credits

This bug was reported by `nrv` via bounty@ethereum.org, who has gracefully requested that the bounty rewards be donated to Médecins sans frontières.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ethereum](https://github.com/ethereum/go-ethereum)

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-wjxw-gh3m-7pm5
- https://nvd.nist.gov/vuln/detail/CVE-2022-29177
- https://github.com/ethereum/go-ethereum/pull/24507
- github.com/ethereum/go-ethereum
