# [C] 7.1 Draining All Ether Provisions of Mangrove

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

Makers can retract their offer by calling retractOffer(). This function accepts the boolean parameter
deprovision which allows the maker to choose to either deprovision the offer or not.

Deprovisioning an offer credits back the provision to the maker. At the same time it must be ensured that
this offer is removed from the offerbook and its gasprice must be set to 0 as the offer is no longer
provisioned.

Not all possible cases are handled correctly inside function retractOffer(). For offers that are not live
(this means they have a 0 amount for offer.gives) the provision can be credited back to the maker
without the offer's gasprice being set to zero.

Hence retractOffer() with deprovision set to true can be executed successfully repeatedly.
Consequently a maker can reclaim more provision than he initially paid for the offer. This bug allows to
eventually drain all Ether of Mangrove.

An offer can easily reach offers.gives = 0 which means it is considered to not be live:

- By calling retractOffer() with bool deprovision set to false, dirtyDeleteOffer() is
    executed. This call sets offer.gives to zero however without setting offer.gasprice to zero
    due to deprovision being false.
- After the offer has been consumed by an order offer.gives is 0.


Code Corrected:

The call to dirtyDeleteOffer() was moved out of the isLive scope. Hence whenever
deprovision is set to true and the provision is credited back to the Maker, the order is deprovisioned.
Calling the function repeatedly on the same offer no longer allows to drain Ether of Mangrove, the issue
has been resolved.
