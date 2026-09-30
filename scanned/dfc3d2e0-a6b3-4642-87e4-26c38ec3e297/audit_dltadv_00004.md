# [H] go-ethereum vulnerable to DoS via malicious p2p message

## Summary
Severity: High
Advisory: GHSA-4xc9-8hmq-j652
Aliases: CVE-2024-32972, GO-2024-2819
Package: github.com/ethereum/go-ethereum
Published: 2024-05-06
Source: https://osv.dev/vulnerability/GHSA-4xc9-8hmq-j652
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.13.15

## Details
### Impact

A vulnerable node can be made to consume very large amounts of memory when handling specially crafted p2p messages sent from an attacker node.

In order to carry out the attack, the attacker establishes a peer connections to the victim, and sends a malicious `GetBlockHeadersRequest` message with a `count` of  `0`, using the `ETH` protocol. 

In `descendants := chain.GetHeadersFrom(num+count-1, count-1)`, the value of `count-1` is passed to the function `GetHeadersFrom(number, count uint64)` as parameter `count`. Due to integer overflow, `UINT64_MAX` value is then passed as the `count` argument to function `GetHeadersFrom(number, count uint64)`. This allows an attacker to bypass `maxHeadersServe` and request all headers from the latest block back to the genesis block. 

### Patches

The fix has been included in geth version `1.13.15` and onwards. 

The vulnerability was patched in: https://github.com/ethereum/go-ethereum/pull/29534

### Workarounds

No workarounds have been made public. 

### References

No more information is released at this time.

### Credit

This issue was disclosed responsibly by DongHan Kim via the Ethereum bug bounty program. Thank you for your cooperation.

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-4xc9-8hmq-j652
- https://nvd.nist.gov/vuln/detail/CVE-2024-32972
- https://github.com/advisories/GHSA-4xc9-8hmq-j652
- https://github.com/ethereum/go-ethereum
- https://github.com/ethereum/go-ethereum/compare/v1.13.14...v1.13.15
