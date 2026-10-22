# [H] Use safeMath for Space contract

## Summary
Severity: High
Contest weight: 0.1124
Dataset id: 15007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
onJoinPool() is high risk, as it could mint a large amount of tokens and other locations in Space.sol.
The safe contract builds on Balancer contracts and thus uses solidity 0.7.x.
However, the math operations in solidity 0.7.x can underflow and overflow. The safe contract doesn’t have sufficient protection against this.

## Recommendation
Use safeMath functions for all addition, subtraction, multiplication and divisions, from for example Open Zeppelin SafeMath.sol or Balancer Math.sol libraries for solidity 0.7.x.
