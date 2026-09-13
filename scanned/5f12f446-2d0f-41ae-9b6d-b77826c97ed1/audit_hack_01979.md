# [M] 6.36 Use of Libraries

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Mellow Finance often uses own custom code for which battle proof libraries exist. We highly recommend
using libraries instead of custom implementations. Especially, when dealing with complex DeFi projects
like Uniswap V3.

Code Corrected:

The code part were most issues were found was the Uniswap oracle. In Version 3 Mellow Finance
switched to the libraries provided by uniswap to interact with the oracle.
