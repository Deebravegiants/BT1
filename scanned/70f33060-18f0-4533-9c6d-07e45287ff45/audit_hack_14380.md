# [H] Malicious users can spam `Minted` events during and after the auction by sending '0' as the amount to mint

## Summary
Severity: High
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L126-L169
Type: audit-issue

## Details
# Malicious users can spam `Minted` events during and after the auction by sending '0' as the amount to mint

## Summary
The contract `MeritDutchAuction` permits to successfully call method `mint` without raising an exception if the argument `amount` given is 0. This could lead to a malicious user spamming `Minted` events during and after the auction by only paying gas fees.

## Vulnerability Detail
As we know the contract `MeritDutchAuction` will be strongly dependent on offchain integrations, and so events play a big role to the protocol. In particular the event `emit Minted(msg.sender, amount, pricePaid);` which will be used for offchain integrations.

## Impact
It is possible to mint 0, causing `Minted` events to be spammed and for this last reason the vulnerability is considered with High score instead of Medium

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L126-L169

## Tool used

Manual Review

## Recommendation
Insert a require checking that the argument `amount` is not equal to 0.
