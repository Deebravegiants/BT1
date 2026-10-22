# [M] Proposer can submit malicious data that can prevent disputes

## Summary
Severity: Medium
Contest weight: 0.5625
Dataset id: 17682
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A proposer can submit malicious data that forces dispute attempts to be reverted, thus preventing disputes (and is therefore able to submit a malicious value unless push() is called).
Oct 3rd to Oct 5th.
There are 2 ways in which a malicious proposer can force a dispute transaction to revert.
1. ABI Decoding
The data cannot be decoded to uint80 dataRoundId and uint64 dataRoundTimestamp.
(Eg. data = 0x).
```solidity
// Retrieve the round data from Chainlink
(uint80 dataRoundId, uint64 dataRoundTimestamp) = abi.decode(
    data,
    (uint80, uint64)
);
```
2. Malicious dataRoundId
The dataRoundId used is out of range (eg. a future dataRoundId or low dataRoundId).
```solidity
(
    ,
    int256 roundValue,
    ,
    uint256 roundTimestamp,
) = AggregatorV3Interface(feed).getRoundData(dataRoundId);
```
Proposals with malicious dataRoundId cannot be disputed. While this can partially be nevertheless be able to continue submitting these malicious proposals as his bond cannot be removed, causing DoS of the shift() and dispute() functionality.

## Recommendation
Wrap the decode and getRoundData() calls in a try-catch block; the validity of the proposal should be set to false in the catch block.
t() where reverting is ok and the chainlink call is wrapped in a try-catch where a revert will lead to a successful dispute.
