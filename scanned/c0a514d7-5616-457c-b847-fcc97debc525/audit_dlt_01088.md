# [M] Weight not properly refunded after EVM execution

## Summary
Severity: Medium
Chain: pallet-ethereum
Component: pallet-ethereum
CVE: CVE-2022-39242
CWE: Incorrect Calculation
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-v57h-6hmh-g2p4
Type: github-advisory

## Details
### Impact

Previously, the worst case weight was always accounted as the block weight for all cases. In case of large EVM gas refunds, this can lead to block spamming attacks -- the adversary can construct blocks with transactions that have large amount of refunds or unused gases with reverts, and as a result inflate up the chain gas prices. This issue is fixed by properly refund unused weights after each EVM execution.

The impact of this issue is limited in that the spamming attack would still be costly for any adversary, and it has no ability to alter any chain state. 

### Patches

The issue is fixed in https://github.com/paritytech/frontier/pull/851

### Workarounds

None.

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Frontier repo](https://github.com/paritytech/frontier/issues)
* Email [Wei](mailto:wei@that.world)
