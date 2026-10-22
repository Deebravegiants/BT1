# [M] (previously M-05)

## Summary
Severity: Medium
Contest weight: 0.1921
Dataset id: 19698
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When there are multiple new phases at L63, they will all start with round.roundId.
As a result, sync() -> getRoundCount() will revert, as the startingRoundId of the last phase for the next phase can be larger than its latestRoundId.
https://github.com/equilibria-xyz/perennial-mono/blob/e801b6eecae6ca609597710d2980bd26184a2ef8/packages/perennial-oracle/contracts/ChainlinkFeedOracle.sol#L58-L76
https://github.com/equilibria-xyz/perennial-mono/blob/e801b6eecae6ca609597710d2980bd26184a2ef8/packages/perennial-oracle/contracts/types/ChainlinkAggregator.sol#L59-L76

## Proof of Concept
Given:
Last phase: 3
Last phase startingRoundId: (uint256(3) << 64) + 1
Last phase latestRoundId: (uint256(3) << 64) + 3
Last phase startingVersion: 10
Current phase: 5
Current aggregator roundId: 1
Current proxy roundId: (uint256(5) << 64) + 1
L63, the first iterate:
The second iterate, L65 startingRoundId: (uint256(5) << 64) + 1;
ChainlinkAggregator.sol#L74, latestRoundId: (uint256(4) << 64) + 1;
ChainlinkAggregator.sol#L75, latestRoundId - startingRoundId will revert.

## Recommendation
Consider adding a parameter startingRoundIds and validate them:
Partial Fix: https://github.com/equilibria-xyz/perennial-mono/pull/110
Our fix here is for us to explicitly revert if trying to sync more than 1 phase in a `sync`.
Identifying the starting round ID for intermediary phases is something we will try to fix in our next oracle update, but for now we will rely on off-chain mechanisms to update the rounds soon after the Chainlink update occurs.
