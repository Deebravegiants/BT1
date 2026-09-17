# [M] Execute on same context checks in VM

## Summary
Severity: Medium
Chain: MultiversX
Component: multiversx/mx-chain-go
CVE: CVE-2022-36061
Published: 2022-08-29
Source: https://github.com/multiversx/mx-chain-go/security/advisories/GHSA-mv8x-668m-53fg
Type: github-advisory

## Details
### Impact
Read only calls between contracts can generate smart contracts results.
For example, if contract A calls in read only mode contract B and the called function will make changes upon the contract's B state, the state will be altered for contract B as if the call was not made in the read-only mode. This can lead to some effects not designed by the original smart contracts programmers.

### Patches
Patch v1.3.35 or higher

### Workarounds
No workaround

### References
For future reference and understanding of this issue, anyone can check this integration test https://github.com/ElrondNetwork/elrond-go/blob/8e402fa6d7e91e779980122d3798b2bf50892945/integrationTests/vm/txsFee/asyncESDT_test.go#L452 that proves the fix and prevents a future code regression. 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in elrond-go ([http://github.com/ElrondNetwork/elrond-go/issues](https://github.com/ElrondNetwork/elrond-go/issues))
