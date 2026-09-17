# [M] Sequencer is incorrectly validated without checking for the GRACE_PERIOD

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592
Type: audit-issue

## Details
# Sequencer is incorrectly validated without checking for the GRACE_PERIOD

## Summary
Sequencer is incorrectly validated without checking for the GRACE_PERIOD

## Vulnerability Detail

According to Chainlink docs about the sequencer in Arbitrum: https://docs.chain.link/data-feeds/l2-sequencer-feeds : 
```text
When the sequencer comes back up after an outage, wait for the GRACE_PERIOD_TIME to pass before accepting answers from the data feed. Subtract startedAt from block.timestamp and revert the request if the result is less than the GRACE_PERIOD_TIME.
If the sequencer is up and the GRACE_PERIOD_TIME has passed, the function retrieves the latest answer from the data feed using the dataFeed object.
```
As you can see in `unstoppable` code, it is checked that the sequencer is up:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592

but it is not checked that the GRACE_PERIOD_TIME has passed, which will cause `unstoppable` to get incorrect/stale prices while the `GRACE_PERIOD_TIME` has not yet been over


## Impact
`GRACE_PERIOD_TIME` has not yet been over will cause `unstoppable` to get stale prices.


## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L588-L592
## Tool used

Manual Review

## Recommendation
This is how it would look to check the grace period in solidity:

```solidity

uint256 private constant GRACE_PERIOD_TIME = 3600;
 error GracePeriodNotOver();

function isSequencerActive() internal view returns (bool) {
    (, int256 answer, uint256 startedAt,,) = sequencer.latestRoundData();
    if (block.timestamp - startedAt <= GRACE_PERIOD_TIME || answer == 1)
        return false;
    return true;
}

```
