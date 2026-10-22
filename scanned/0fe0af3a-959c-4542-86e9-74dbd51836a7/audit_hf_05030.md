# [M] BorrowerNFT can mint at most 65536 NFTs which

## Summary
Severity: Medium
Contest weight: 0.2124
Dataset id: 23032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BorrowerNFT limits NFT counter to 2 bytes or max value of 65536:
function _INDEX_SIZE() internal pure override returns (uint256) {
    return 2;
}
Once this counter value is reached (65536 NFTs minted), the mint call will always revert:
require((totalSupply = totalSupply_ + qty) < _MAX_SUPPLY(), "MAX_SUPPLY");
...
function _MAX_SUPPLY() internal pure returns (uint256) {
    return (1 << (_INDEX_SIZE() << 3));
}
The value of 65536 is not that large, especially given that BorrowerNFT is specifically designed for multiple mints. For example, if each user mints 10 borrowers on average, only 6553 users can mint NFTs, and if the userbase grows larger, all new users will be denied the service due to mint revert. Alternatively, an attacker can simply mint all 65536 NFTs to harm the protocol and deny service to new protocol users. This will cost only gas and about 1-2 days for the attacker (10 mints per 12-seconds block).
BorrowerNFT limits NFT counter to 2 bytes (at max 65536 NFTs can be minted):
y/src/borrower-nft/BorrowerNFT.sol#L55-L57
Internal pre-conditions
65536 NFTs minted
External pre-conditions
None
Attack Path
1. 65536 NFTs minted in the protocol (either in the normal protocol operation, or by attacker)
2. Any new user tries to call mint which now always reverts, preventing core protocol functionality and new users joining
Core protocol functionality not working after 65536 NFTs are minted (protocol userbase exceeds about 10000 to 50000 users or attacker spending gas and 1-2 days to spam mint transactions), which sets a small hard cap limit on the number of protocol users, which can not be changed.
core protocol function (mint) to all users.

## Recommendation
Use at least 4-8 bytes for _INDEX_SIZE
