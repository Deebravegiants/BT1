# [M] E5 MitigationConfirmed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/37
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/pools/Pools.sol#L65


# Vulnerability details

## Summary
The provided PR in E5 attempts to limit the number of swaps to one per block to prevent bypassing arbitrage within a single block.

## Analysis
The changes made in the PR like [this one](https://github.com/othernet-global/salty-io/commit/2d1b7df004394720c0d8bb4aefe903021631eff3#diff-ac1567b6d6f64912bb3767c9ee5c1991a6555c69fc1d65aa631991cbf9005096R39-R47) or [this](https://github.com/othernet-global/salty-io/commit/2d1b7df004394720c0d8bb4aefe903021631eff3#diff-ac1567b6d6f64912bb3767c9ee5c1991a6555c69fc1d65aa631991cbf9005096R71-R79) are not present in the [final codebase](https://github.com/code-423n4/2024-03-saltyio-mitigation.git) given as part of the audit. 

Although the codebase contains modifications on top of the PR, the PR achieves the task of implementing what it set out to. 
It must additionally be said that in this particular case even though the final codebase is not exactly the same as the PR, it still contains the correct logic too albeit with different modifier & variable names. So the effect of the mismatch is negligible.

## Conclusion
LGTM









## Assessed type

Other
