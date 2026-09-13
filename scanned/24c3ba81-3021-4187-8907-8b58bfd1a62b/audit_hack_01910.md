# [H] 6.2 Wrong Calculation of Locked Provision

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected


When a user updates their offer through Forwarder.updateOffer, MangroveOrder tries to calculate
the new gas price by calling deriveGasprice. The gas price depends on the total provision available
for this order. That is the sum of the extra provision attached which is stored in args.fund and the
already locked provision. Currently, the locked amount is calculated with the following snippet:

```
vars.offerDetail.gasprice() * 10 ** 9 * args.gasreq + vars.local.offer_gasbase()
```
This formula is wrong for two reasons:

```
1.It depends on args.gasreq which is the updated gas requirement of the order as passed by
the user.
2.There are parentheses missing around args.gasreq + vars.local.offer_gasbase(),
as this entire term should be multiplied by the gas price.
```
This miscalculation can have multiple consequences:

```
1.Can allow users to steal funds (see relevant issue).
2.An order can be submitted with smaller gasprice since the calculated total provision is too
small.
```
Code Corrected:

Forwarder.updateOffer has been updated. Currently, users can only increase the provision for an
order. Users cannot determine args.gasreq as it is set to be equal to the offerGasreq(). It is
important to notice that offerGasreq() is not constant but depends on the configuration of the
MangroveOrder and in particular the gas requirements of the router.
