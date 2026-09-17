# [?] miner: fix deadlock and panic issues in block production (#1639)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2025-07-16
Source: https://github.com/0xPolygon/bor/commit/95d00c9b182f76011f59adc77924e94a53a7b99f
Type: security-commit

## Details
miner: fix deadlock and panic issues in block production (#1639)

- Skip stale sealed blocks that are behind current chain head to prevent
    resultLoop from attempting to write outdated blocks after reorgs
  - Add 1-second timeout to chDeps channel send to prevent indefinite
    blocking when receiver is dead or channel is full
  - Return error when transaction count exceeds dependency list length
    to prevent array index out of bounds panic

  These fixes address production issues where mining nodes would deadlock
  for hours after milestone-triggered reorgs, unable to
  process new blocks or respond to chain updates.
