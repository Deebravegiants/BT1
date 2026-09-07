# [M] Pool._addPoolMetrics(uint256) is subject to potential miner manipulation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-07-spartan
Published: 2021-07-21
Source: https://github.com/code-423n4/2021-07-spartan-findings/issues/201
Type: code-finding

## Details
# Handle

heiho1


# Vulnerability details

## Impact

Pool._addPoolMetrics(uint256) on line 334 relies on block.timestamp and is potentially vulnerable to miner manipulation.  This could lead to erroneous pool metrics.

## Proof of Concept

https://github.com/code-423n4/2021-07-spartan/blob/e2555aab44d9760fdd640df9095b7235b70f035e/contracts/Pool.sol#L338

https://solidity-by-example.org/hacks/block-timestamp-manipulation/

## Tools Used

Slither

## Recommended Mitigation Steps

An external time oracle like ChainLink Alarm Clock is worth consideration: https://blog.chain.link/blockchain-voting-using-a-chainlink-alarm-clock-oracle/
