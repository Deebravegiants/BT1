# [H] 5.1.9 changeSpotPriceAndDelta()only uses ERC721 version ofbalanceOf().

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** StandardSettings.sol#L227-L

**Description:** The functionchangeSpotPriceAndDelta()usesbalanceOf()with one parameter. This is the
ERC721 variant. In order to support ERC1155, a second parameter of the NFTidhas to be supplied.

```
function changeSpotPriceAndDelta(address pairAddress, ...) public {
...
if ((newPriceToBuyFromPair < priceToBuyFromPair) && pair.nft().balanceOf(pairAddress) >= 1) {
...
}
}
```
**Recommendation:** Detect the use of ERC1155 and use the appropriatebalanceOf()version.

**Sudorandom Labs:** Solved in PR#30.

**Spearbit:** Verified that this is fixed by PR#30.
