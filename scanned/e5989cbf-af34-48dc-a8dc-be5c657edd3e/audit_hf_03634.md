# [M] No check for active Arbitrum and optimistic

## Summary
Severity: Medium
Contest weight: 0.5547
Dataset id: 19703
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol wants to deploy Arbitrum and optimism
Chainlink recommends that all Optimistic L2 oracles consult the Sequencer Uptime
Feed to ensure that the sequencer is live before trusting the data returned by
If the Arbitrum Sequencer goes down, oracle data will not be kept up to date, and
thus could become stale. However, users are able to continue to interact with the
protocol directly through the L1 optimistic rollup contract. You can review Chainlink
docs on L2 Sequencer Uptime Feeds for more details on this.
As a result, users may be able to use the protocol while oracle feeds are stale. Then
outdated price can be used to settle trade.
If the Arbitrum or optimism sequencer goes down, the protocol will allow users to
continue to operate at the previous (stale) rates.

## Recommendation
We recommend add the sequencer active check
```solidity
function isSequencerActive() internal view returns (bool) {
    (, int256 answer, uint256 startedAt,,) = sequencer.latestRoundData();
    if (block.timestamp - startedAt <= GRACE_PERIOD_TIME || answer == 1)
        return false;
    return true;
}
```
and
```solidity
if (!isSequencerActive()) revert Errors.L2SequencerUnavailable();
```
