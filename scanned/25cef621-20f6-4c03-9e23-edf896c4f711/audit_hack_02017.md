# [M] 7.2 L2 Addresses

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected


The address format can differ across L2 systems / different domains the DAI wormhole connects. While
the majority work with address of 20 bytes, compatible with the solidity address type, other systems can
use other address format. One example of those is StarkNet where addresses of are of type felt which
are larger than 20 bytes.

Code corrected:

The receiver and operator fields of the WormholeGUID struct have been replaced by bytes
types to accommodate for address formats up to 32 bytes.
