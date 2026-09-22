# [?] Moved event subscription out of go func to avoid race condition where in the event broadcast was completed even before the subscription was done in go

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys/quorum
Published: 2019-11-04
Source: https://github.com/Consensys/quorum/commit/118ccc6e8f60e3345d573a2533833aee47755c85
Type: security-commit

## Details
Moved event subscription out of go func to avoid race condition where in the event broadcast was completed even before the subscription was done in go func, resulting in permissions service not starting for the node. (#866)
