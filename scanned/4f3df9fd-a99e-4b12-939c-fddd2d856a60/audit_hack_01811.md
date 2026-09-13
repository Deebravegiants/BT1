# [M] A new malicious adapter can access users' tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The purpose of the `MetaSwap` contract is to save users gas costs when dealing with a number of different aggregators. They can just `approve()` their tokens to be spent by `MetaSwap` (or in a later architecture, the `Spender` contract). They can then perform trades with all supported aggregators without having to reapprove anything.

A downside to this design is that a malicious (or buggy) adapter has access to a large collection of valuable assets. Even a user who has diligently checked all existing adapter code before interacting with `MetaSwap` runs the risk of having their funds intercepted by a new malicious adapter that's added later.

#### Recommendation

There are a number of designs that could be used to mitigate this type of attack. After discussion and iteration with the client team, we settled on a pattern where the `MetaSwap` contract is the only contract that receives token approval. It then moves tokens to the `Spender` contract before that contract `DELEGATECALL`s to the appropriate adapter. In this model, newly added adapters shouldn't be able to access users' funds.
