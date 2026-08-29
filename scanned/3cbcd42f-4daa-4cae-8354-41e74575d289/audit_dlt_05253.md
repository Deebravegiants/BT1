# [?] [bugfix] fix text overflow on paper wallet

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2021-03-20
Source: https://github.com/dogecoin/dogecoin/commit/dfb78d26dc38cf86783ec0161408c593556337d6
Type: security-commit

## Details
[bugfix] fix text overflow on paper wallet

- use Courier instead of "monospace" as font family as the latter
  does not translate to an actual monospace font properly
- make address and privkey fields to have equal dimensions and
  margins, because their fontsizes are calculated uniformly too
- make the max font size 98% of the wallet, instead of 99%
