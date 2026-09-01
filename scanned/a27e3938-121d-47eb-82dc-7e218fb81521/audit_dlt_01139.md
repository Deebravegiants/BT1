# [?] graphql: add query depth limit to prevent DoS attacks (#32344)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-08-19
Source: https://github.com/ethereum/go-ethereum/commit/1c74f2376167f50a4b7ece730c472309d7611362
Type: security-commit

## Details
graphql: add query depth limit to prevent DoS attacks (#32344)

## Summary

This PR addresses a DoS vulnerability in the GraphQL service by
implementing a maximum query depth limit. While #26026 introduced
timeout handling, it didn't fully mitigate the attack vector where
deeply nested queries can still consume excessive CPU and memory
resources before the timeout is reached.

## Changes
- Added `maxQueryDepth` constant (set to 20) to limit the maximum
nesting depth of GraphQL queries
- Applied the depth limit using `graphql.MaxDepth()` option when parsing
the schema
- Added test case `TestGraphQLMaxDepth` to verify that queries exceeding
the depth limit are properly rejected

## Security Impact

Without query depth limits, malicious actors could craft deeply nested
queries that:
  - Consume excessive CPU cycles during query parsing and execution
  - Allocate large amounts of memory for nested result structures
- Potentially cause service degradation or outages even with timeout
protection

This fix complements the existing timeout mechanism by preventing
resource-intensive queries from being executed in the first place.

## Testing

Added `TestGraphQLMaxDepth` which verifies that queries with nesting
depth > 20 are rejected with a `MaxDepthExceeded` error.

## References
  - Original issue: #26026
- Related security best practices:

_Trimmed to 38 lines — full report: https://github.com/ethereum/go-ethereum/commit/1c74f2376167f50a4b7ece730c472309d7611362_
