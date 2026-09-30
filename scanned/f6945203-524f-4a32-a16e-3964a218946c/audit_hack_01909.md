# [H] 6.1 Locked Refunded Provision

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

When a maker submits an order to the Mangrove orderbook, they need to provide some ETH, also
known as the provision, to compensate the takers in case the makerExecute hook reverts. A maker can
update their offer by calling Forwarder.updateOffer. Note that at this point a maker can update most
of the parameters of the order including gasreq, i.e. the gas required for the makerExecute hook to
execute. A maker could reduce the gas requirements meaning that some provision will be refunded to
them. Forwarder.updateOffer does not handle this refunding (the ownerData.weiBalance is not
updated) and Mangrove system only sees MangroveOrder as a maker. This means that the refunded
amount is essentially lost for the end-user of the MangroveOrder. Note that if the provision needs to be
increased again, the end-user must provide extra ETH.

Code Corrected:

In the current implementation, the provision can only be increased therefore no funds are locked.
