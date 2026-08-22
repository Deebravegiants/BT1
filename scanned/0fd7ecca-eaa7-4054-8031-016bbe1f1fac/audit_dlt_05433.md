# [?] Fix race condition between election creation and vote_cache triggering (#4610)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-05-09
Source: https://github.com/nanocurrency/nano-node/commit/9cd662cc702ded070395f0c9610c75414bcbcaeb
Type: security-commit

## Details
Fix race condition between election creation and vote_cache triggering (#4610)

The vote_cache is triggered after an election is created, and specifically after the active_elections mutex is released, which causes a race condition when checking the votes in an election.
