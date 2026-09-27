# [?] fix: avoid panic when fork schedule is empty (#16175)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-12-23
Source: https://github.com/OffchainLabs/prysm/commit/dd05e44ef38990c9236332e354b5c9bf146004c8
Type: security-commit

## Details
fix: avoid panic when fork schedule is empty (#16175)

SortedForkSchedule should never be empty for a properly initialized
network schedule, but the handler already had a branch to support an
empty result. Without an early return, we wrote a JSON response and then
still accessed schedule[0], which could panic and double-write the HTTP
response in misconfigured setups.

---------

Co-authored-by: Radosław Kapka <rkapka@wp.pl>
