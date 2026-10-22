# [M] 7.4 Inverted Token Performance

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The signature of the function is:

_getTokenPerformance(uint256 initialPrice, uint256 latestPrice)

and computes the performance ratio as latestPrice / initialprice. However, the function is
always called with the arguments in the following order (latestPrice_param,
initialPrice_param), the result of the call will yield the inverted performance ratio
initialPrice_param / latestPrice_param.

Code corrected:

Natspec and _getTokenPerformance call input order was fixed.
