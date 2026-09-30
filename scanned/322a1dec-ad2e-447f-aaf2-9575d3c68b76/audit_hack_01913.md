# [M] 6.5 Users Can Steal Funds From MangroveOrder

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The core Mangrove system maintains the balanceOf mapping which stores how much ETH is available
for each maker to be used as a provision for their orders. Importantly, the MangroveOrder contract is
seen as one single maker by the system, even though there might be many end users creating their
orders through it. Let us assume that at some point the balance of MangroveOrder is positive and an
attacker has already submitted an order. It is possible as we show in another issue that there might be
some non-claimable balance since updateOrder does not handle refunds. An attacker can steal money
from mangrove by employing any of the following two vectors:

```
1.Updating an order without sending funds:
```
- The attacker calls Forwarder.updateOrder for their order with msg.value == 0 and
    they increase the gas requirement of their order.
- This means that args.fund == 0 so gas price will remain the same, however, the total
    provision needed has been increased as the gas requirements have been increased!
- At this point MGV.updateOffer is called with msg.value == 0.


- Mangrove core does not perform any check if there are enough funds attached to the call
    since it relies on the balanceOf mapping by calling debitWei.
- Mangrove core uses the amount stored in balanceOf for the extra provision.
- The attacker now retracts the order and withdraws the provision of the order which
    includes the stolen amount.

```
2.Updating an order by attaching funds:
```
- The attacker calls Forwarder.updateOrder for their order with msg.value != 0 and
    they increase the gas requirement of their order.
- Since funds have been attached to the transaction, the gas price will be recalculated.
- The new provision at this point is calculated wrongly since the provision parameter
    passed to derivePrice depends on args.gasreq which represents the updated gas
    requirements of the offer and not vars.offerDetail.gasreq(). Note that
    args.gasreq can be freely set by the users so arbitrarily large value could be passed. As
    a result, the new gas price is greater than it should be but the extra funds passed are not
    enough to cover for the extra provision needed by the offer.
- Mangrove core uses the amount stored in balanceOf for the extra provision.
- The attacker now retracts the order and withdraws the provision of the order which
    includes the stolen amount.

A similar attack can be performed when some of the global parameters change, which could result in
inaccurate accounting of provisions. If the gasbase of the token pair related to an order changes in the
core mangrove system, calling updateOffer can result in an increased (or decreased) provision
without providing any additional funds. This will credit (or debit) funds to the MangroveOrder contract
which aren't attributed to any user. In particular, if the global gas price is increased, calling
updateOffer of Mangrove core with an unchanged gasprice which is lower than the new global gas
price, the mangrove core system will set the gas price higher without receiving any funds. This again
changes the balance of the MangroveOrder contract, without attributing it to any individual user. While
_newOffer and _updateOffer in Forwarder have checks to make sure the offer's gas price is higher
than the global gas price, __posthookSuccess__ in MangroveOffer does not. Hence, if the global gas
price changes, then an order is partially filled and attempts to repost, its provision will be increased with
no additional submitted funds. While the amounts of funds are small, it is conceivable that a malicious
user could be able to exploit a change in the global gas price or the gasbase in order to steal funds.

It is important to note that this issue cannot result in users losing funds since the excessive provision
which can be stolen cannot be claimed by any specific user. In the normal case, no excessive provision
should be available. Therefore, it is expected the amount that can be stolen to be low. Hence, we
consider the issue as medium severity.

Code partially corrected:

The issue has been addressed in multiple different ways:

```
1.In the current implementation there shouldn't be unallocated users' funds in Mangrove core.
```
```
2.Users can only increase the provision of an order using MangroveOrder.updateOrder, not
decrease it. Hence, they must provide additional provision and can not submit orders which
could make use of funds that are already stored in the Mangrove core.
3.The __posthookSuccess__ uses Forwarder._updateOffer.
```
