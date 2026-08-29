# [M] Possible miner incentive for chain reorgs if ETHBlockDelay is too small

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-07
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/12
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

## Impact
If ETHBlockDelay is too small and the incentive for miners is large enough, it would profitable for miners to attempt
to double spend by depositing assets, waiting for confirmation on the cosmos-SDK and then reorging the blockchain.

Although an attack like this has never been done, it could potentially cost hundreds of millions of dollars in damages. With MEV at all time highs and miners regularly using custom geth implementations its not totally out
of the question to see an attack similar to this happening soon.

## Recommended Mitigation Steps
The best way to avoid something like this is to make sure to wait for a large number of blocks until a transaction is confirmed by the cosmos system.
