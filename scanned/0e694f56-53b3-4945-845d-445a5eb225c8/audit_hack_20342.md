# [M] **5.2.13 Fewer checks in** pairTransferNFTFrom() **and** pairTransferERC1155From() **than in** pairTransfer-

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
ERC20From()

**Severity:** Medium Risk

**Context:** LSSVMRouter.sol#L491-L543, VeryFastRouter.sol#L344-L

**Description:** The functionspairTransferNFTFrom()andpairTransferERC1155From()don't verify that the cor-
rect type of pair is used, whereaspairTransferERC20From()does. This means actions could be attempted on the
wrong type of pairs. These could succeed for example if a NFT is used that supports both ERC721 and ERC1155.

Note: also see issue"pairTransferERC20Fromonly supports ERC721 NFTs"

The following code is present in bothLSSVMRouterandVeryFastRouter.

```
function pairTransferERC20From(...) ... {
require(factory.isPair(msg.sender, variant), "Not pair");
...
require(variant == ILSSVMPairFactoryLike.PairVariant.ERC721_ERC20, "Not ERC20 pair");
...
}
function pairTransferNFTFrom(...) ... {
require(factory.isPair(msg.sender, variant), "Not pair");
...
}
function pairTransferERC1155From(...) ... {
require(factory.isPair(msg.sender, variant), "Not pair");
...
}
```
**Recommendation:** Add comparable checks as inpairTransferERC20From()to the functionspairTransferNFT-
From()andpairTransferERC1155From().

**Sudorandom Labs:** Solved in PR#30.

**Spearbit:** Verified that this is fixed by PR#30.
