# [M] Processing: fallback search of SCRs when not found in the main cache

## Summary
Severity: Medium
Chain: MultiversX
Component: multiversx/mx-chain-go
CVE: CVE-2022-46173
Published: 2022-12-23
Source: https://github.com/multiversx/mx-chain-go/security/advisories/GHSA-p228-4mrh-ww7r
Type: github-advisory

## Details
### Impact
Processing issue, nodes are affected when trying to process a cross-shard relayed transaction with a smart contract deploy transaction data. The problem was a bad correlation between the transaction caches and the processing component. If the above-mentioned transaction was sent with more gas than required, the smart contract result (SCR transaction) that should have returned the leftover gas, would have been wrongly added to a cache that the processing unit did not consider. The node stopped notarizing metachain blocks. The fix was actually to extend the SCR transaction search in all other caches if it wasn't found in the correct (expected) sharded-cache. 

### Patches
All versions >= v1.3.50 will contain this patch

### Workarounds
For the moment there is no workaround

### References
N/A

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [elrond-go main repo](https://github.com/ElrondNetwork/elrond-go)
