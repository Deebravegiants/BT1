# [?] Fix Forkchoice panic (#16728)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-05-19
Source: https://github.com/OffchainLabs/prysm/commit/441cfe0ad6be0d09c57a3485c7696dd622021f92
Type: security-commit

## Details
Fix Forkchoice panic (#16728)

This PR adds a fix for a forkchoice panic whenever there are orphaned
blocks in the end of an epoch. We removed children of empty nodes but
not full nodes.

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>
Co-authored-by: terence <terence@prysmaticlabs.com>
