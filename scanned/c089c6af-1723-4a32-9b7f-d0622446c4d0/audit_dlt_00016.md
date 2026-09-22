# [M] Ethash DAG generation bug can cause miners to create invalid PoW

## Summary
Severity: Medium
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2020-26240
Published: 2020-11-24
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-v592-xf75-856p
Type: github-advisory

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
