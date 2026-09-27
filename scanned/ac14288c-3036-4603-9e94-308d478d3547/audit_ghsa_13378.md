# [M] Tokenizer vulnerable to client brute-force of token secrets

## Summary
Severity: Medium
Advisory: GHSA-f28g-86hc-823q
Ecosystem: Go
Published: 2023-07-13
Source: https://github.com/advisories/GHSA-f28g-86hc-823q
Type: github-advisory

## Affected
- Go: `github.com/superfly/tokenizer` — affected >=0 <0.0.1

## Details
### Impact

Authorized clients, having an `inject_processor` secret, could brute-force the secret token value by abusing the `fmt` parameter to the `Proxy-Tokenizer` header.

### Patches

This was fixed in https://github.com/superfly/tokenizer/pull/8 and further mitigated in https://github.com/superfly/tokenizer/pull/9.

## References
- https://github.com/superfly/tokenizer/security/advisories/GHSA-f28g-86hc-823q
- https://github.com/superfly/tokenizer/pull/8
- https://github.com/superfly/tokenizer/pull/9
- https://github.com/superfly/tokenizer
