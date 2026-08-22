# [?] core/vote: prevent vote pool DOS (#684)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2025-02-13
Source: https://github.com/axieinfinity/ronin-archive/commit/3d30c056636df6e9b97a25eeb06d03699ee5f8ed
Type: security-commit

## Details
core/vote: prevent vote pool DOS (#684)

* core/vote: only track originated peer if vote is valid

* core/vote: prune peer feature vote counter if reached threshold

* core/vote: blocking put vote flow, verify vote target number
