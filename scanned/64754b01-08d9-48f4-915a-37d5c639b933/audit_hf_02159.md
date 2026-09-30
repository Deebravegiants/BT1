# [H] Potential Repeated acceptBid() For The Same Offer

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 12075
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, when the borrower intends to use his assets as collateral to borrow other assets, he should create an offer for his assets with the call to createOffer(), while others can bid for the offer with the call to offerBid() by providing the type of the loanable asset, amount, interest rate, time duration, etc. After that, the acceptBid() is called by the borrower to accept one of the bids that he is interested in. By doing so, he can borrow the bid related assets. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the DealManager contract. In the acceptBid() function, this requirement of require(_offer.maker == address(msg.sender), "AcceptBid: account not maker") (line 408) is executed to ensure only the owner of the offer (specified by the input _offerId parameter) can accept the bid, and the next requirement of require(_bid.status == OfferBidStatus.Open, "AcceptBid: bid is already canceled") (line 409) is executed to ensure the validity of the bid (specified by the input _bidId parameter). However, we notice it doesn't check whether the offer has accepted a bid before, which may be exploited by a malicious actor to accept other bids for the same offer again and again. Given this, we suggest to add necessary sanity check at the beginning of the acceptBid() function to prevent this case as follows: require(_offer.status == OfferStatus.Pending).
```solidity
function acceptBid(
    uint256 _offerId,
    uint256 _bidId,
    uint256 _safeDuration
) external nonReentrant {
    require(_offerId < totalOffersCount, "AcceptBid: offer not found");
    Offer storage _offer = offers[_offerId];
    OfferBidInfo storage _bid = offerBids[_offer.id][_bidId];
    require(_offer.maker == address(msg.sender), "AcceptBid: account not maker");
    require(_bid.status == OfferBidStatus.Open, "AcceptBid: bid is already canceled");
    require(block.timestamp > _bid.updatedAt + _safeDuration, "AcceptBid: bid is recently updated");
    // Set offer
```

## Recommendation
Add the above-mentioned sanity check inside the acceptBid() routine.
