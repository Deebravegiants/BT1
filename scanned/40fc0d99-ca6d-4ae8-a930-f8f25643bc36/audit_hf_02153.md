# [M] Improper Logic Of viewBidsPerOffer()

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 12056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, Feeder Lending protocol implements an auction mechanism to provide lending, borrowing and liquidating services. When the borrower intends to use his assets as collateral to borrow other assets, he should create an offer for his assets. Others can bid for the offer by providing the type of the loanable asset, amount, interest rate, time duration, etc. Once the borrower accepts one of the bids, he will receive the bid related assets. If the borrower cannot repay the borrowed assets on time, his collateral will be liquidated. Feeder Lending protocol also provides a series of query routines for the user. In particular, one routine, i.e., DealManager::viewBidsPerOffer(), is designed to query the bids information of an offer. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the DealManager contract. The DealManager::viewBidsPerOffer() routine has three input parameters: the first _offerId parameter specifies the queried offer identification, the second _cursor parameter specifies the start index of the offerBids[_offerId] array, and the third _size parameter indicates the number of the offerBids[_offerId] array element starting from _cursor. However, we notice the returned _values copies from 0 of the offerBids[_offerId] array rather than _cursor (line 510). Given this, we suggest to improve the implementation as below: _values[i] = offerBids[_offerId][_cursor + i] (line 510).
```solidity
function viewBidsPerOffer(
    uint256 _offerId,
    uint256 _cursor,
    uint256 _size
) external view returns (OfferBidInfo[] memory, uint256) {
    uint256 _length = _size;
    uint256 _bidsLength = offerBids[_offerId].length;
    if (_length > _bidsLength - _cursor) {
        _length = _bidsLength - _cursor;
    }
    OfferBidInfo[] memory _values = new OfferBidInfo[](_length);
    for (uint256 i = 0; i < _length; i++) {
        _values[i] = offerBids[_offerId][i];
    }
    return (_values, _cursor + _length);
}
```
Note other routines, i.e., DealManager::viewBidsPerBidder(), DealManager::viewOffers(), DealManager::viewOffersByCollateral(), FeedLoan::viewLoans(), FeedLoan::viewLoansPerLender(), and FeedLoan::viewLoansPerBorrower(), share the same issue.

## Recommendation
Correct the implementation of above-mentioned routines.
