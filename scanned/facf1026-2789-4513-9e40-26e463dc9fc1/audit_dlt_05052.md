# [C] Processing: MultiESDTNFTTransfer call on a SC address with missing function name

## Summary
Severity: Critical
Chain: MultiversX
Component: multiversx/mx-chain-go
CVE: CVE-2022-36058
Published: 2022-08-29
Source: https://github.com/multiversx/mx-chain-go/security/advisories/GHSA-qf7j-25g9-r63f
Type: github-advisory

## Details
### Impact
Anyone who uses elrond-go to process blocks (historical or actual) that contains a transaction like this: `MultiESDTNFTTransfer@01@54444558544b4b5955532d323631626138@00@0793afc18c8da2ca@` (mind the missing function name after the last `@`)
Basic functionality like p2p messaging, storage, API requests and such are unaffected.

### Patches
Patch v1.3.34 or higher

### Workarounds
No workarounds

### References
For future reference, one can observe the following integration test:
[[provide the link to the integration test]](https://github.com/ElrondNetwork/elrond-go/blob/8e402fa6d7e91e779980122d3798b2bf50892945/integrationTests/vm/txsFee/asyncESDT_test.go#L402)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in elrond-go (http://github.com/ElrondNetwork/elrond-go/issues)
