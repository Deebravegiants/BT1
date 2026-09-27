# [?] store: Fix race condition in tests

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-03-28
Source: https://github.com/graphprotocol/graph-node/commit/53b64050eba0a6282564b37b396620b1d965d3fd
Type: security-commit

## Details
store: Fix race condition in tests

Tests wait for the queue to be empty to see the result of changes; the code
previously emptied the queue before a possible error had been recorded,
which would cause test failures.
