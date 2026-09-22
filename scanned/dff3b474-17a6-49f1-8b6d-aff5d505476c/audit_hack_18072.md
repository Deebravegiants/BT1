# [M] Potential  block timestamp manipulation vulnerability

## Summary
Severity: Medium
Reporter: Decent Gingham Bear
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Potential  block timestamp manipulation vulnerability

## Summary
Block Timestamp Manipulation

## Vulnerability Detail
The contract uses block.timestamp to validate Chainlink oracle freshness. Miners could manipulate this timestamp.

## Impact
Attacker can make stale oracle prices seem valid, resulting in incorrect pricing.


## Code Snippet

 
``` solidity

require(block.timestamp - updatedAt <= heartbeatInterval, "ORACLE_HEARTBEAT_FAILED");

```
## Tool used

Manual Review

## Recommendation

Only impacts pricing, not critical contract assets. Other price validations also in place. Difficult for miner to consistently manipulate timestamp.

Use block.number instead of timestamp to validate freshness.

The vulnerability allows some manipulation of price calculations. But other factors limit the impact, so it is be a lower severity issue.
