# [M] 5.3.9 Inconsistent betweenbalanceOfNFT,balanceOfNFTAtand_balanceOfNFTfunctions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VotingEscrow.sol#L985, VotingEscrow.sol#L976
**Description:** ThebalanceOfNFTfunction implements a flash-loan protection that returns zero voting balance if
ownershipChange[_tokenId] == block.number. However, this was not consistently applied to thebalanceOfNF-
TAtand_balanceOfNFTfunctions.
VotingEscrow.sol
function balanceOfNFT(uint256 _tokenId) external view returns (uint256) {
if (ownershipChange[_tokenId] == block.number) return 0;
return _balanceOfNFT(_tokenId, block.timestamp);
}

As a result, Velodrome or external protocols calling thebalanceOfNFTandbalanceOfNFTAtexternal functions will
receive different voting balances for the same veNFT depending on which function they called.
Additionally, the internal_balanceOfNFTfunction, which does not have flash-loan protection, is called by the
VotingEscrow.getVotesfunction to compute the voting balance of an account. TheVotingEscrow.getVotes
function appears not to be used in any in-scope contracts, however, this function might be utilized by some exter-
nal protocols or off-chain components to tally the votes. If that is the case, a malicious user could flash-loan the
veNFTs to inflate the voting balance of their account.
**Recommendation:** If the requirement is to have all newly transferred veNFTs (ownershipChange[_tokenId] ==
block.number) have zero voting balance to prevent someone from flash-loaning veNFT to increase their voting
balance, the flash-loan protection should be consistently implemented across all the related functions.
**Velodrome:** I think the current status of this issue is that once timestamp governance is merged in, block-based
balance functions will be removed as the contract will adopt timestamps as its official "clock" (see EIP6372). Once
it is merged, we will assess the consistency of ownership_change on the various fns.
**Spearbit:** Acknowledged.
