# [M] 5.2.17 ImprovedexAllowlist

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SwapperV2.sol#L67-L81, Swapper.sol#L65-L78, LibAccess.sol#L13-L15, DexManagerFacet.sol, Ac-
cessManagerFacet.sol
**Description:** The functions_executeSwaps()of bothSwapperV2.solandSwapper.soluse a whitelist to make
sure the right functions in the allowed dexes are called. The checks forapproveTo,callToandsignature
(callData) are independent. This means that anysignatureis valid for any dex combined with anyapproveTo
address. This grands more access than necessary.
This is important because multiple functions can have the same signature. For example these two functions have
the same signature:

- gasprice_bit_ether(int128)


- transferFrom(address,address,uint256)
See bytes4_signature=0x23b872dd Note: brute forcing an innocent looking function is straightforward
ThetransferFrom()is especially dangerous because it allows sweeping tokens from other users that have set
an allowance for the LiFi Diamond. If someone gets a dex whitelisted, which contains a function with the same
signature then this can be abused in the current code.
Present in bothSwapperV2.solandSwapper.sol:

```
function _executeSwaps(...) ... {
if (
!(appStorage.dexAllowlist[currentSwapData.approveTo] &&
appStorage.dexAllowlist[currentSwapData.callTo] &&
appStorage.dexFuncSignatureAllowList[bytes32(currentSwapData.callData[:8])])
) revert ContractCallNotAllowed();
}
}
```
**Recommendation:** In the whitelisting managerDexManagerFacet.sol, combine thedex_address,approveTo
andsignatureas a set and whitelist them as a triple. Adapt the rest of the code (e.g. SwapperV2.soland
Swapper.sol) to match that.
Note: the libraryLibAccess, which does something similar already stores the duoexecutor addressandsigna-
ture.
For extra safety: before whitelisting, double check the function signatures using 4byte.directory or sig.eth.samczun,
both for theDexManagerFacet.solandAccessManagerFacet.sol.
**LiFi:** We vet all of the DEX addresses before we add to our whitelist and and quit a few of them share the same
functions. We acknowledge the risk and plan to mitigate through careful vetting of our whitelist. This should avoid
selector collisions.
**Spearbit:** Acknowledged, careful checking prevents the issue.
