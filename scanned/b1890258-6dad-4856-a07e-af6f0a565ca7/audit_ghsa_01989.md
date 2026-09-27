# [M] Denial of service in github.com/ethereum/go-ethereum

## Summary
Severity: Medium
Advisory: GHSA-r33q-22hv-j29q
CVE: CVE-2020-26264
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-r33q-22hv-j29q
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.9.25

## Details
### Impact

A DoS vulnerability can make a LES server crash via malicious `GetProofsV2` request from a connected LES client.

### Patches

The vulnerability was patched in https://github.com/ethereum/go-ethereum/pull/21896. 

### Workarounds

This vulnerability only concerns users explicitly enabling `les` server; disabling `les` prevents the exploit. 
It can also be patched by manually applying the patch in https://github.com/ethereum/go-ethereum/pull/21896. 


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ethereum](https://github.com/ethereum/go-ethereum)
* Email us at [security@ethereum.org](mailto:security@ethereum.org)

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-r33q-22hv-j29q
- https://nvd.nist.gov/vuln/detail/CVE-2020-26264
- https://github.com/ethereum/go-ethereum/pull/21896
- https://github.com/ethereum/go-ethereum/commit/bddd103a9f0af27ef533f04e06ea429cf76b6d46
- https://github.com/ethereum/go-ethereum
- https://github.com/ethereum/go-ethereum/releases/tag/v1.9.25
- https://pkg.go.dev/vuln/GO-2021-0063
