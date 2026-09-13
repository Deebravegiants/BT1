# [H] Gas griefing on MeritDutchAuction contract

## Summary
Severity: High
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163
Type: audit-issue

## Details
# Gas griefing on MeritDutchAuction contract

## Summary
An attacker can do gas griefing attack on MeritDutchAuction contract resulting in a loss for the smart contract. 

## Vulnerability Detail
The `MeritDutchAuction.mint` function manages the edge case when too much ETH was sent by the client and so a refund the difference happens on https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163 . Because no gas limit was set then an attacker might use this to perform gas griefing on `MeritDutchAuction`, and even more, if the attacker reverts the refund operation as it will lead to the `nft.mint` calls on https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159  to revert, all at the expense of `MeritDutchAuction`.

## Impact
An attacker could potentially cause significant losses to `MeritDutchAuction`.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L126-L169

## Tool used

Manual Review

## Recommendation
A possible solution should be to separate the minting logic from the refund operation, then the refund operation should send the amount of ETH via call method by setting a gas limit
