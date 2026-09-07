# [H] github.com/MANTRA-Chain/mantrachain/x/tokenfactory tx gas limit is not enforced in send hooks

## Summary
Severity: High
Advisory: GHSA-qwvm-wqq8-8j69
CVE: CVE-2025-61595
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-qwvm-wqq8-8j69
Type: github-advisory

## Affected
- Go: `github.com/MANTRA-Chain/mantrachain/v4` — affected >=0 <4.0.2
- Go: `github.com/MANTRA-Chain/mantrachain/v3` — affected >=0
- Go: `github.com/MANTRA-Chain/mantrachain/v2` — affected >=0
- Go: `github.com/MANTRA-Chain/mantrachain` — affected >=0

## Details
### Impact

send hooks can spend more gas than what's remained in tx, combined with recursive calls in the wasm contract, can amplify the gas consumption exponentially.

### Patches

It's patched in v4.0.2 and v5.0.0

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

## References
- https://github.com/MANTRA-Chain/mantrachain/security/advisories/GHSA-qwvm-wqq8-8j69
- https://nvd.nist.gov/vuln/detail/CVE-2025-61595
- https://github.com/MANTRA-Chain/mantrachain/issues/432
- https://github.com/MANTRA-Chain/mantrachain/commit/30d36c46e9823b56b8f0dcbb66e980ca5df284e4
- https://github.com/MANTRA-Chain/mantrachain
- https://pkg.go.dev/vuln/GO-2025-3997
