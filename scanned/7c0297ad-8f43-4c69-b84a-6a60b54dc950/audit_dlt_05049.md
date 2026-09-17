# [H] Add processIfTxErrorCrossShard on metaChain transaction processor

## Summary
Severity: High
Chain: MultiversX
Component: multiversx/mx-chain-go
CVE: CVE-2023-33964
Published: 2023-05-29
Source: https://github.com/multiversx/mx-chain-go/security/advisories/GHSA-7xpv-4pm9-xch2
Type: github-advisory

## Details
### Impact
Metachain cannot process a cross-shard miniblock.
An invalid transaction with the wrong username on metachain is not treated correctly on the metachain transaction processor. This is strictly a processing issue that could have happened on MultiversX chain. If an error like this had occurred, the metachain would have stopped notarizing blocks from the shard chains. The resuming of notarization is possible only after applying a patched binary version. 
 
### Patches
Introduce processIfTxErrorCrossShard for metachain transaction processor. 

### Workarounds
No

### References
No
