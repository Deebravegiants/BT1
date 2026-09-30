# [M] 6.3 Expiration Date Cannot Be Updated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

A user can update most of the offer details by calling Forwarder.updateOffer. However, the
expiration date cannot be changed. In order to change the expiration date of an order, one must retract it
and submit a new one.

Code Corrected:

MangroveOrder.setExpiry has been added to allow users to update the expiration date of the order.
