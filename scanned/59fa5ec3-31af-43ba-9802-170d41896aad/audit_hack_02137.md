# [M] Missing input validation in realise()

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-07-spartan/blob/main/contracts/Synth.sol#L187
Type: audit-issue

## Details
# Handle

0xsanson


# Vulnerability details

## Impact
In synth.sol, the function `realise(pool)` can be called using any existing pool as input. From my understanding, it's supposed that `pool` and `synth` must have the same underlying token. With the current implementation an user can call various synth contracts with the same target pool, and burn LP tokens which aren't suppose to.

## Proof of Concept
https://github.com/code-423n4/2021-07-spartan/blob/main/contracts/Synth.sol#L187

## Tools Used
editor

## Recommended Mitigation Steps
Check if the protocol design wants the situation described above. If not, add a require(pool.TOKEN == LayerONE).
