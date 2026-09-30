# [M] 5.2.11 Functioncall()is risky and can be restricted further

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** LSSVMPair.sol#L640-L

**Description:** The functioncall()is powerful and thus risky. To reduce the risk it can be restricted further by dis-
allowing potentially dangerous function selectors. This is also a step closer to introducing permissionless routers.

```
function call(address payable target, bytes calldata data) external onlyOwner {
ILSSVMPairFactoryLike _factory = factory();
require(_factory.callAllowed(target), "Target must be whitelisted");
(bool result,) = target.call{value: 0}(data);
require(result, "Call failed");
}
```

**Recommendation:** Filter out unwanted function selectors, for example for the following functions:pairTransfer-
ERC20From(),pairTransferNFTFrom(),pairTransferERC1155From(),onOwnershipTransferred()

**Sudorandom Labs:** Solved in PR#44.

**Spearbit:** Verified that this is fixed by PR#44.
