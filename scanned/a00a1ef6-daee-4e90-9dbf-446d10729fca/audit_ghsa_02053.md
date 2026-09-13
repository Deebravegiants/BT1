# [M] Erroneous Proof of Work calculation in geth

## Summary
Severity: Medium
Advisory: GHSA-v592-xf75-856p
CVE: CVE-2020-26240
CWE: CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-v592-xf75-856p
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.9.24

## Details
### Impact
An ethash mining DAG generation flaw in Geth could cause miners to erroneously calculate PoW in an upcoming epoch (estimated early January, 2021). This happened on the ETC chain on 2020-11-06. This issue is relevant only for miners, non-mining nodes are unaffected.

### Patches
This issue is also fixed as of 1.9.24. Thanks to @slavikus for bringing the issue to our attention and writing the fix. 

### Workarounds
This PR implements a patch: https://github.com/ethereum/go-ethereum/pull/21793 

### References
https://blog.ethereum.org/2020/11/12/geth_security_release/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ethereum](https://github.com/ethereum/go-ethereum)
* Email us at [security@ethereum.org](mailto:security@ethereum.org)

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-v592-xf75-856p
- https://nvd.nist.gov/vuln/detail/CVE-2020-26240
- https://github.com/ethereum/go-ethereum/pull/21793
- https://github.com/ethereum/go-ethereum/commit/d990df909d7839640143344e79356754384dcdd0
- https://blog.ethereum.org/2020/11/12/geth_security_release
- https://github.com/ethereum/go-ethereum
