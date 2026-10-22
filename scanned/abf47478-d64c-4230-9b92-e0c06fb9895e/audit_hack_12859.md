# [M] Not waiting for a grace period after the Sequencer is up can lead to wrong oracle prices

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592
Type: audit-issue

## Details
# Not waiting for a grace period after the Sequencer is up can lead to wrong oracle prices

## Summary
Not waiting for a grace period after the Sequencer is up can lead to wrong oracle prices, causing several issues in the protocol.

## Vulnerability Detail
There are two things to check in the Sequencer based in the official [Chainlink docs and examples](https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code):
1. If it is up
2. If a grace period after the Sequencer is up is over

The `Vault` contract uses the Chainlink price feeds to get the USD values for different tokens and thus it checks first if the sequencer is up. But the problem it is not also checking if the grace period is over:

```vyper
@view
@internal
def _sequencer_up() -> bool:
    # answer == 0: Sequencer is up
    # answer == 1: Sequencer is down
    answer: int256 = ChainlinkOracle(ARBITRUM_SEQUENCER_UPTIME_FEED).latestRoundData()[1]
    return answer == 0
```

Similar issues: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/3

## Impact
It can lead to wrong and stale data, causing different issues in the protocol.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592

## Tool used
Manual Review

## Recommendation
Check also if the grace period is over:
```vyper
+ GRACE_PERIOD_TIME: uint256 = 3600;
@view
@internal
def _sequencer_up() -> bool:
    # answer == 0: Sequencer is up
    # answer == 1: Sequencer is down
-    answer: int256 = ChainlinkOracle(ARBITRUM_SEQUENCER_UPTIME_FEED).latestRoundData()[1]
+  round_id: uint80 = 0
+  answer: int256 = 0
+  started_at: uint256 = 0
+  updated_at: uint256 = 0
+  answered_in_round: uint80 = 0
+  round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(ARBITRUM_SEQUENCER_UPTIME_FEED).latestRoundData()

+  if block.timestamp - started_at <= GRACE_PERIOD_TIME or answer == 1:
+      return false
+  return true
-    return answer == 0
```
