# [C] Elrond-go has improper initialization

## Summary
Severity: Critical
Advisory: GHSA-mv8x-668m-53fg
CVE: CVE-2022-36061
CWE: CWE-665
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-mv8x-668m-53fg
Type: github-advisory

## Affected
- Go: `github.com/ElrondNetwork/elrond-go` — affected >=0 <1.3.35

## Details
### Impact
Read only calls between contracts can generate smart contracts results. For example, if contract A calls in read only mode contract B and the called function will make changes upon the contract's B state, the state will be altered for contract B as if the call was not made in the read-only mode. This can lead to some effects not designed by the original smart contracts programmers.

### Patches
Patch v1.3.35 or higher

### Workarounds
No workaround

### References
For future reference and understanding of this issue, anyone can check this integration test https://github.com/ElrondNetwork/elrond-go/blob/8e402fa6d7e91e779980122d3798b2bf50892945/integrationTests/vm/txsFee/asyncESDT_test.go#L452 that proves the fix and prevents a future code regression. 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in elrond-go ([http://github.com/ElrondNetwork/elrond-go/issues](https://github.com/ElrondNetwork/elrond-go/issues))

## References
- https://github.com/ElrondNetwork/elrond-go/security/advisories/GHSA-mv8x-668m-53fg
- https://nvd.nist.gov/vuln/detail/CVE-2022-36061
- https://github.com/ElrondNetwork/elrond-go
- https://github.com/ElrondNetwork/elrond-go/blob/8e402fa6d7e91e779980122d3798b2bf50892945/integrationTests/vm/txsFee/asyncESDT_test.go#L452
- https://github.com/ElrondNetwork/elrond-go/releases/tag/v1.3.35
