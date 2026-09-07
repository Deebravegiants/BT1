# [?] execution: fix potential limitedBigJump calc uint underflow in updateForkChoice (#15746)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-06-25
Source: https://github.com/erigontech/erigon/commit/29378d42dfb874d88bf91ce84b924b47253ff13e
Type: security-commit

## Details
execution: fix potential limitedBigJump calc uint underflow in updateForkChoice (#15746)

protects the `limitedBigJump` calculation from a uint64 underflow 

e.g. there can be cases (for example on chains like bor) where the ufc
header number is a few blocks less than the previous exec progress from
the last ufc - if we are on block 10 on fork A but then block 9 on fork
B appears with higher difficulty

such an underflow can cause limitedBigJump to be set to `true` which
then sets `IsInitialCycle=true` potentially causing furious/aggressive
prunes on chain tip
