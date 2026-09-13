# [M] 5.2.6 Owner can mislead users by abusingchangeSpotPrice()andchangeDelta()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** LSSVMPair.sol#L584-L

**Description:** A malicious owner could set up a pair which promises to buy NFTs for high prices. As soon as
someone tries to trade, the owner could frontrun the transaction by setting the spotprice to 0 and gets the NFT for
free. BothchangeSpotPrice()andchangeDelta()can be used to immediately change trade parameters where
the aftereffects depends on the curve being used.

Note: TheswapNFTsForToken()parameterminExpectedTokenOutputandswapTokenForSpecificNFTs()param-
etermaxExpectedTokenInputprotect users against sudden price changes. But users might not always set them
in an optimal way.

A design goal of the project team is that the pool owner can quickly respond to changing market conditions, to
prevent unnecessary losses.

```
function changeSpotPrice(uint128 newSpotPrice) external onlyOwner {
```
```
}
function changeDelta(uint128 newDelta) external onlyOwner {
```
```
}
```
**Recommendation:** Consider introducing a small delay of 1 or 2 blocks to prevent frontrunning. It could be done,
for example, with 2 functions :announce(newSpotPrice)which registers timestamp + new price and emits an
event (for transparency) followed by the existingchangeSpotPrice()which checks if current timestamp > n blocks
after the previously announced timestamp.

**Sudorandom Labs:** Acknowledged, callers should usemaxInputandminOutputto protect themselves.

**Spearbit:** Acknowledged.
