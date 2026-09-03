# [M] Wrong logic in L2 sequencer check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-21
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/5
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Oracle.sol#L360-L362


# Vulnerability details

## C4 issue
ADD-02: [Missing L2 sequencer checks for Chainlink oracle](https://github.com/code-423n4/2024-03-revert-lend-findings/issues/12)

## Impact
- If `sequencerUptimeFeed` is set, then the function will revert most of the time and affect a lot of other functions in Revert Lend.

## Proof of concept
The original issue is fixed by [PR #27](https://github.com/revert-finance/lend/pull/27)
The mitigation code adds sequencer check as follows:
```solidity
// sequencer check on chains where needed
        if (sequencerUptimeFeed != address(0)) {
            (, int256 sequencerAnswer, uint256 startedAt,,) =
                AggregatorV3Interface(sequencerUptimeFeed).latestRoundData();

            // Answer == 0: Sequencer is up
            // Answer == 1: Sequencer is down
            if (sequencerAnswer == 0) {
                revert SequencerDown();
            }

            // Make sure the grace period has passed after the
            // sequencer is back up.
            uint256 timeSinceUp = block.timestamp - startedAt;
            if (timeSinceUp <= SEQUENCER_GRACE_PERIOD_TIME) {
                revert SequencerGracePeriodNotOver();
            }
        }
```
However, as you can see in the comment `sequencerAnswer == 0` indicates that the sequencer is up, yet in that case the code reverts with `SequencerDown` error (wrong logic). This logic is also stated in the [docs](https://docs.chain.link/data-feeds/l2-sequencer-feeds):
`The message calls the updateStatus function in the ArbitrumSequencerUptimeFeed contract and updates the latest sequencer status to 0 if the sequencer is up and 1 if it is down`.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/5_
