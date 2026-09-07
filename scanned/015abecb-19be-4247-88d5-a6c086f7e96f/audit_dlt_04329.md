# [M] Payer in Stream.sol is not capable of calling the Stream#cancel, Stream#withdraw and Stream#resuceERC20

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/21
Type: sherlock-finding

## Details
ctf_sec

medium

# Payer in Stream.sol is not capable of calling the Stream#cancel, Stream#withdraw and Stream#resuceERC20

## Summary

Payer in Stream.sol is not capable of calling the Stream#cancel, Stream#withdraw and Stream#resuceERC20

## Vulnerability Detail

I want to quote from the doc:

#### Creating a DAO proposal with Streamer

> First the user (in our case the DAO's web UI) calls predictStreamAddress to get the future stream contract address.
Then a proposal can be composed with the following two transactions:

> StreamFactory.createStream(...), where the new stream's address should match predictStreamAddress
Payer.sendOrRegisterDebt(...), where the payment recipient is the address from predictStreamAddress
Once executed, the Token Buyer and Payer contracts work together to fund the new stream asynchronously, and once funded the stream's recipient can withdraw their streamed funds.

the assumption is that the payer address is

https://github.com/nounsDAO/token-buyer/blob/main/src/Payer.sol

In Stream.sol, Stream#cancel, Stream#withdraw is restricted by the modifier  onlyPayerOrRecipient

```solidity
    /**
     * @dev Reverts if the caller is not the payer or the recipient of the stream.
     */
    modifier onlyPayerOrRecipient() {
        if (msg.sender != recipient() && msg.sender != payer()) {
            revert CallerNotPayerOrRecipient();
        }

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/21_
