# [?] fix(eth): remove non-deterministic behaviour from eth keeper (#432)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-04-29
Source: https://github.com/axelarnetwork/axelar-core/commit/5adbee6cec35f0747343ab15e7248ea1e682653c
Type: security-commit

## Details
fix(eth): remove non-deterministic behaviour from eth keeper (#432)

GetDeposit iterated over a map to get the correct deposit. While it was deterministic for our logic (exactly one case would be hit), it's possible that the kvstore in the background spent different amounts of gas on different nodes. This commit removes the loop over the map in favour of rolling out all cases.
