# [M] Bid and Auction Limits Allow Participants to Lock Out All Competition

## Summary
Severity: Medium
Contest weight: 0.1214
Dataset id: 14667
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current settings of MAX_BID_COUNT and MAX_OFFER_COUNT in TermAuctionBidLocker and TermAuctionOfferLocker
prevent bids and offers past a certain count. In the current code, these values need to be relatively low: they are both
set to 1,000 (although may need to be lower: see TRM2-03). It would be possible for an auction participant to submit
many tiny bids in a single transaction and thus lock out all other participants.
One bidder could call TermAuctionBidLocker::lockBids() multiple times in a single transaction to create 999 tiny bids
and one large bid, all at the minimum level. At this point, only one bidder exists, but no others can enter the auction.
This issue is mitigated by the fact that the offerers could withdraw their offers or the auction could be cancelled.

## Recommendation
Consider changing the auction resolution logic to be significantly more gas efficient so that these limits are not needed.
