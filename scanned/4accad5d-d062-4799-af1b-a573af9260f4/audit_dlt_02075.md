# [?] graph, store: Fix potential race condition in BoundedQueue.clear()

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-03-18
Source: https://github.com/graphprotocol/graph-node/commit/224196b89904b1aa8fb7f5867f7cf4e6f54ff38d
Type: security-commit

## Details
graph, store: Fix potential race condition in BoundedQueue.clear()

Rather than clearing the queue by removing entries in bulk, which could
race against a pop at the same time, clear the queue by popping one entry
at a time.
