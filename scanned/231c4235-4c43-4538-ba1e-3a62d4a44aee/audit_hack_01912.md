# [M] 6.4 Underflow in postRestingOrder

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

Once the market order part of GTC order has been filled as much as possible, the remaining amount the
user wants to trade is put into a resting order. Note that if fillWants == true, then the Mangrove
engine will have stopped matching the order either when it is fully filled, there are no more orders on the
books, or when the total average price of the order would fall below the threshold of the ratio between the
order's initial wants and gives. Hence, if the matching stops before the order's wants are fully filled, we
are guaranteed not to have given away more than the order initially had (else the total average price
would be below what we initially wanted).


However, if fillWants == false, this condition no longer holds. The order can receive arbitrarily
many tokens before giving away all the tokens it has to give away. As the price of a trade is defined by
the maker, there could be orders on the books which give away arbitrarily many tokens for a very low
price. Hence, the user can receive more tokens in the market order part of the trade than they were
expecting to. As such, res.takerGot + res.fee can exceed tko.takerWants despite only having
partially filled the order.

When we go to post a resting order, the following code is executed:

```
res.offerId = _newOffer(
OfferArgs({
outbound_tkn: outbound_tkn,
inbound_tkn: inbound_tkn,
wants: tko.makerWants - (res.takerGot + res.fee), // tko.makerWants is before slippage
gives: tko.makerGives - res.takerGave,
gasreq: offerGasreq() + additionalGasreq, // using default gasreq of the strat + potential admin defined increase
gasprice: 0, // ignored
pivotId: tko.pivotId,
fund: fund,
noRevert: true, // returns 0 when MGV reverts
owner: msg.sender
})
);
```
When the wants for the resting order are calculated, an underflow can occur in the case described
above, as the market order part of the GTC order could have received arbitrarily many tokens. As Solidity
0.8.10 is used, this will simply revert the transaction, but will unnecessarily prevent the user from
completing their trade.

Specification Changed:

Currently, the order is posted with the same price as the taker originally wanted. Thus, the issue has
been mitigated.

Giry SAS replied:

```
this problem made use reevaluate our specification: requiring the (instant) market order and the
(asynchronous) maker order to respect a limit average price is not well defined. In some cases this
would lead the maker order to be posted for a 0 price. We decided to change the specification and
post the maker order at the price initially set by the taker for the market order (irrespectively of the
obtained price).
```
