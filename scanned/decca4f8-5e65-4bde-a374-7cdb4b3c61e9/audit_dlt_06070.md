# [?] fix: don't crash pindexer on blocks without a timestamp (#4764)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2024-07-26
Source: https://github.com/penumbra-zone/penumbra/commit/47a1ba1a2cb8ad18a6271bbe380eb32da3d56024
Type: security-commit

## Details
fix: don't crash pindexer on blocks without a timestamp (#4764)

## Describe your changes

this sets timestamp to default for blocks without one to

## Issue ticket number and link

fixes https://github.com/penumbra-zone/penumbra/issues/4761

## Checklist before requesting a review

- [x] If this code contains consensus-breaking changes, I have added the
"consensus-breaking" label. Otherwise, I declare my belief that there
are not consensus-breaking changes, for the following reason:

indexer changes only
