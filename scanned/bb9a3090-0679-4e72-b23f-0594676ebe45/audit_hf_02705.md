# [H] Auctions Require Too Much Gas to Complete

## Summary
Severity: High
Contest weight: 0.1733
Dataset id: 14666
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The gas usage of the TermAuction function completeAuction() uses approximately 1.5m gas for every 10 bids and
offers in the auction. It is therefore estimated to reach the block gas limit at approximately 200 bids and offers.
Note that, at a gas price of 100 wei, the block gas limit of 30m gas would cost 3 ether.
The current settings of MAX_BID_COUNT and MAX_OFFER_COUNT in TermAuctionBidLocker and TermAuctionOfferLocker
are both 1,000. The block gas limit would be reached significantly before this limit, and therefore they would not have
their stated effect of preventing the block gas limit from preventing auction completion.

## Recommendation
Consider changing the auction resolution logic to be significantly more gas efficient. Alternatively, set these limits to
180.
