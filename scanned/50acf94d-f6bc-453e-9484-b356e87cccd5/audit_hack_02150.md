# [M] Downcasting Can Freeze The Chain

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

nascent


# Vulnerability details

# [M-01] Downcasting Can Freeze The Chain
**Severity: Medium**
**Likelihood: Low**

The function `utils::downcast_uint256() -> Option<u64>` returns `None` if the input value is greater than `U64MAX`.  If the value being downcast is read from a contract (e.g. a nonce), and the contract could be put into such a state where a `Uint256` is set to higher value, this will cause all nodes to halt execution upon reading this value, requiring a patch to reenable the bridge.

## Recommendation
Change the signature of `downcast_uint256()` to return a `Result<>`, and/or remove any `unwrap()`s of the result.
