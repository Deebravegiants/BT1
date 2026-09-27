# [C] 6.2 ORDER_TYPEHASH Is Incorrect

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Critical Version 1 Code Corrected

The ORDER_TYPEHASH in OrderStructs does not equal the actual encoded data in
Hashing.hashOrder. It is used to calculate an EIP-712 compliant hash for an order which is then used
to recover the signer of the given order. Since the typehash is incorrect, this mechanism will not work for
correctly signed orders.

Code correct

OrderStructs.ORDER_TYPEHASH is now computed at compile time on the correct structure signature.
