# [?] Fix bf.unset(u64::MAX) causing delayed panic on bf.ranges()

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2022-03-29
Source: https://github.com/filecoin-project/ref-fvm/commit/35fc054bcde416098f5a0f46b412ed1ab033556b
Type: security-commit

## Details
Fix bf.unset(u64::MAX) causing delayed panic on bf.ranges()

Detected by rle_encode fuzz target.
Caused by overflow when trying to compute input ranges into difference
operation within `ranges()`.

Signed-off-by: Jakub Sztandera <kubuxu@protocol.ai>
