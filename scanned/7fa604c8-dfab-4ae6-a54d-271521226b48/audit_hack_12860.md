# [M] Vault: should have a grace period after sequencer is up

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592
Type: audit-issue

## Details
# Vault: should have a grace period after sequencer is up

## Summary

Oracle only checks if sequence is up but does not check for how long it has been up. If sequencer went down and prices changed significantly. Mass liquidation could happen when it goes up. Should provide a grace period to allow customers to react to such an event.

## Vulnerability Detail

Only checks if sequencer is active.

```python
def _sequencer_up() -> bool:
    # answer == 0: Sequencer is up
    # answer == 1: Sequencer is down
    answer: int256 = ChainlinkOracle(ARBITRUM_SEQUENCER_UPTIME_FEED).latestRoundData()[1]
    return answer == 0
```

## Impact

Unfair liquidation to borrowers when this happens.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592

## Tool used

Manual Review

## Recommendation

Have a grace period for customers to react to such event.
