# [M] Public `createStream()` without restrictions allows spam of event `StreamCreated()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/46
Type: sherlock-finding

## Details
zimu

medium

# Public `createStream()` without restrictions allows spam of event `StreamCreated()`

## Summary
Public `StreamFactory.createStream()` can be called by anyone, and the input checks are easily fulfilled without restrictions hard to satisfy. Then spam of `StreamFactory.createStream()` with massive emitted `StreamCreated()` events can happen.

## Vulnerability Detail
Anyone can create stream with the input checks fulfilled in the following `createStream()`, which allows spam of `StreamFactory.createStream()` with event `StreamCreated()` emitted.
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
        if (payer == address(0)) revert PayerIsAddressZero();
        if (recipient == address(0)) revert RecipientIsAddressZero();
        if (tokenAmount == 0) revert TokenAmountIsZero();
        if (stopTime <= startTime) revert DurationMustBePositive();
        if (tokenAmount < stopTime - startTime) revert TokenAmountLessThanDuration();

        stream = streamImplementation.cloneDeterministic(
            encodeData(payer, recipient, tokenAmount, tokenAddress, startTime, stopTime),
            salt(
                msg.sender, payer, recipient, tokenAmount, tokenAddress, startTime, stopTime, nonce
            )
        );
        IStream(stream).initialize();

        emit StreamCreated(
            msg.sender, payer, recipient, tokenAmount, tokenAddress, startTime, stopTime, stream
            );
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/46_
