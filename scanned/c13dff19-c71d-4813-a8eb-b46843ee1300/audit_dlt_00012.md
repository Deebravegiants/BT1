# [M] LES Server DoS via GetProofsV2

## Summary
Severity: Medium
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2020-26264
Published: 2020-12-11
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-r33q-22hv-j29q
Type: github-advisory

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
