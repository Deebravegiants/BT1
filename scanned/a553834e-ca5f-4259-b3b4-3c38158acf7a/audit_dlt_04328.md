# [M] Does not check if the Stream.sol#payment token matches the payer#payment token.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/23
Type: sherlock-finding

## Details
ctf_sec

medium

# Does not check if the Stream.sol#payment token matches the payer#payment token.

## Summary

Does not check if the Stream.sol#payment token is the same as the payer#payment token.

## Vulnerability Detail

I want to quote from the doc:

#### Creating a DAO proposal with Streamer

> First the user (in our case the DAO's web UI) calls predictStreamAddress to get the future stream contract address.
Then a proposal can be composed with the following two transactions:

> StreamFactory.createStream(...), where the new stream's address should match predictStreamAddress
Payer.sendOrRegisterDebt(...), where the payment recipient is the address from predictStreamAddress
Once executed, the Token Buyer and Payer contracts work together to fund the new stream asynchronously, and once funded the stream's recipient can withdraw their streamed funds.

The Payer address has a payment token address.

https://github.com/nounsDAO/token-buyer/blob/33171cfbdb52cf9d5bd6520f1baec0b64b2f7168/src/Payer.sol#L39

```solidity
/// @notice The ERC20 token used to pay users
IERC20 public immutable paymentToken;
```

the Stream contract has a payment token as well.

https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/StreamFactory.sol#L202

```solidity
stream = streamImplementation.cloneDeterministic(
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/23_
