# [H] Incorrect Default Permissions in Binance tss-lib

## Summary
Severity: High
Advisory: GHSA-399h-cmvp-qgx5
CVE: CVE-2020-12118
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N/E:U/RL:O/RC:R (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-399h-cmvp-qgx5
Type: github-advisory

## Affected
- Go: `github.com/binance-chain/tss-lib` — affected >=0 <1.2.0

## Details
The keygen protocol implementation in Binance tss-lib before 1.2.0 allows attackers to generate crafted h1 and h2 parameters in order to compromise a signing round or obtain sensitive information from other parties.
### Specific Go Packages Affected
github.com/binance-chain/tss-lib/ecdsa/keygen

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12118
- https://github.com/binance-chain/tss-lib/pull/89
- https://github.com/binance-chain/tss-lib/pull/89/commits/7b7c17e90504d5dad94b938e84fec690bb1ec311
- https://github.com/binance-chain/tss-lib/releases/tag/v1.2.0
