# [M] _validateAndGetPrice() doesn't check If Ar-

## Summary
Severity: Medium
Contest weight: 0.5349
Dataset id: 19940
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
When utilizing Chainlink in L2 chains like Arbitrum, it's important to ensure that the
prices provided are not falsely perceived as fresh, even when the sequencer is
down. This vulnerability could potentially be exploited by malicious actors to gain
an unfair advantage.
There is no check:
could potentially be exploited by malicious actors to gain an unfair advantage.
```

## Recommendation
```solidity
code example of Chainlink:
https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code
```
