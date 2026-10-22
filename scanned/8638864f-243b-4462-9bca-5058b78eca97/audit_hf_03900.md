# [M] FixedStrikeOptionTeller: create can be invoked

## Summary
Severity: Medium
Contest weight: 0.5653
Dataset id: 20192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
block.timestamp == expiry but these option tokens cannot be exercised even in the same transaction. The create function has this statement:
```solidity
if (uint256(expiry) < block.timestamp) revert Teller_OptionExpired(expiry);
```
The exercise function has this statement:
```solidity
if (uint48(block.timestamp) >= expiry) revert Teller_OptionExpired(expiry);
```
Notice the >= operator which means when block.timestamp == expiry the exercise function reverts. So if a user claims his rewards using OTLM.claimRewards or OTLM.claimNextEpochRewards when block.timestamp == expiry, he receives the freshly minted option tokens but he cannot exercise these option tokens even in the same transaction (or same block). Moreover, since the receiver does not possess these freshly minted option tokens, he cannot reclaim them either (assuming reclaim function contains the currently missing optionToken.burn statement). Option token will be minted to user but he cannot exercise them. Receiver cannot reclaim them as he doesn't hold that token amount. This leads to loss of funds as the minted option tokens become useless. Also the scenario of users claiming at expiry is not rare.

## Recommendation
Consider maintaining a consistent timestamp behaviour. Either prevent creation of option tokens at expiry or allow them to be exercised at expiry.
