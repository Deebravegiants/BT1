# [?] fix(pathfinder/sync): prevent underflow in block time metrics

## Summary
Severity: Unknown
Chain: Starknet
Component: eqlabs/pathfinder
Published: 2025-12-16
Source: https://github.com/equilibriumco/pathfinder/commit/5bc5a555c4d132e72fec2722a3aee0ff84de7e4b
Type: security-commit

## Details
fix(pathfinder/sync): prevent underflow in block time metrics

After an L2 reorg it's possible that `latest_timestamp` is greater than
the timestamp of the next block being processed. This would cause an
underflow when calculating the block time difference, leading to a panic
in the sync consumer task.
