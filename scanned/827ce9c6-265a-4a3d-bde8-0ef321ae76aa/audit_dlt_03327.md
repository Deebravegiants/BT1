# [M] Large ValSets potentially freezes `Gravity.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-07
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/9
Type: code-finding

## Details
# Handle

nascent


# Vulnerability details

Gas requirements of `makeCheckpoint`: If the size of the validator set grows large enough during a time of block-size expansion, it may be possible to make the validator set large enough that, when the block size shrinks, the gas required to perform `makeCheckpoint` may be larger than the amount of gas available in the block. In that case, the validator set could not be updated until the block size increased. If a reduction in upper gas limit for blocks occurs at the miner layer, it may be bricked permanently.
