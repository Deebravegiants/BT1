# [M] 6.1 Cost of bytesToHex

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The bytesToHex is used to convert bytes to hex string. The only reason for this is to be compliant with
the elliptic-js library. The bytesToHex is an extremely inefficient on-chain. Such conversions on-chain
are strongly discouraged. They are computationally expensive and may lead to gas exhaustion. This
does not pose a direct security risk, but it lowers the overall usability and scalability of the contract.

Code corrected:

The RPBS-sol package now operates with the bytes representation directly, without conversion to hex.
The new function encodePoint is used in the assessed contracts instead of encodePointHex
function.
