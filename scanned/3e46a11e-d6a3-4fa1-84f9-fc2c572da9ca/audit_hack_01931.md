# [C] 6.1 Signatures Are Valid for Any Address

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

Signatures.isValidSignature checks the validity of a given order's signature. For signature types
POLY_GNOSIS_SAFE and POLY_PROXY, the code makes sure that an order's maker address belongs to
the same account that signed the order.

This is not true for the signature type EOA. Any account can create a signature for an order that contains
an arbitrary maker address. Since users give token approval to the protocol on order creation, malicious
actors can generate orders for an account that already generated an order, but, for example, with a more
favorable price. This order will then be executable although the account in question did not authorize it.

Code corrected


Signatures.verifyEOASignature has been added, which additionally ensures that the
Order.maker == Order.signer for EOAs.
