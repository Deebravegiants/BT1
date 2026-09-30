# [C] Duplicate Bid and Offer IDs

## Summary
Severity: Critical
Contest weight: 0.3780
Dataset id: 14664
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can overwrite their existing bids, stranding collateral and making auction resolution impossible.
When a new bid is submitted with a bid ID that does not already exist, a new bid ID is generated and used. However,
this new bid ID is determined by the bid submission, and so the same submission always creates the same bid ID.
This makes it possible to overwrite existing bids for the same user. When this happens, the tally of bids is incorrectly
increased and this makes it impossible to either complete or cancel the auction. The user is also unable to unlock their
collateral from the first submission.
The logic for determining the bid ID of a bid submission is contained in _lock():
bool bidExists = bids[bidSubmission.id].amount != 0;
bytes32 bidId;
if (bidExists) {
if (bids[bidSubmission.id].bidder != bidSubmission.bidder) {
revert BidNotOwned();
bidId = bidSubmission.id;
} else {
bidId = _generateBidId(bidSubmission.id, authedUser);
function _generateBidId(
bytes32 id,
address user
) internal view returns (bytes32) {
return keccak256(abi.encodePacked(id, user, address(this)));
As can be seen, if a submission is made with an existing bid ID, the variable bidExists is set to True and the code
proceeds to modify the existing bid. However, if the submission contains a bid ID which does not exist, it deterministically
generates a new bid ID based on only the user’s address and the submitted bid ID. Critically, this generated bid ID is not checked against existing bid IDs.
Because of this, it is possible to generate the same bid ID multiple times. Each time, the variable bidExists will be set to
False, however, and so the bid submission will be treated as a new bid. It will overwrite the existing bid’s information,
transfer new collateral without regard for existing collateral, and increment bidCount, the contract’s counter for the
number of submitted bids.
This last point will make it impossible to either complete or cancel the auction as both of the relevant functions in
TermAuction, completeAuction() and cancelAuction(), call getAllBids() in TermAuctionBidLocker. This function
loops through the submitted bids, processes them, and, crucially, decrements bidCount. If bidCount is not zero after
this loop, it reverts. This revert will always occur in the situation where the number of bids is less than bidCount, as is
the case here.
Term Finance – Smart Contract Changes
In addition, as the functions that unlock bids and return collateral rely on the values stored in bids, and these have
been overwritten, it will not be possible for the user to unlock the collateral from their overwritten bids.
This issue also applies to TermAuctionOfferLocker, which uses similar code.

## Recommendation
Change the logic of _generateBidId() to check that the generated ID does not exist and only return once a unique
bid ID has been generated.
