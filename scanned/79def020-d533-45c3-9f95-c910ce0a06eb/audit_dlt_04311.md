# [M] Protocol can become useless by malicious attackers through front-running

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/60
Type: sherlock-finding

## Details
hansfriese

high

# Protocol can become useless by malicious attackers through front-running

## Summary

A malicious attacker can front-run `createStream()` and deploy the same stream implementation before the protocol and this prevents the stream's initialization, which makes the protocol useless.

## Vulnerability Detail

The `createStream()` function at StreamFactory.sol #L184 clones the stream implementation with data and salt based on the input arguments.
The problem is the stream initialization is called after calling `cloneDeterministic()`.

```solidity
function createStream(
    address payer,
    address recipient,
    uint256 tokenAmount,
    address tokenAddress,
    uint256 startTime,
    uint256 stopTime,
    uint8 nonce
) public returns (address stream) {
    // These input checks are here rather than in Stream because these parameters are written
    // using clone-with-immutable-args, meaning they are already set when Stream is created and can't be
    // verified there. The main benefit of this approach is significant gas savings.
    if (payer == address(0)) revert PayerIsAddressZero();
    if (recipient == address(0)) revert RecipientIsAddressZero();
    if (tokenAmount == 0) revert TokenAmountIsZero();
    if (stopTime <= startTime) revert DurationMustBePositive();
    if (tokenAmount < stopTime - startTime) revert TokenAmountLessThanDuration();

    stream = streamImplementation.cloneDeterministic(
        encodeData(payer, recipient, tokenAmount, tokenAddress, startTime, stopTime),
        salt(
            msg.sender, payer, recipient, tokenAmount, tokenAddress, startTime, stopTime, nonce
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/60_
