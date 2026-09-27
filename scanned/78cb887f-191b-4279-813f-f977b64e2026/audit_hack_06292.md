# [H] Malicious bidder can block any other bidder overtaking him

## Summary
Severity: High
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L164-L167
Type: audit-issue

## Details
# Malicious bidder can block any other bidder overtaking him

## Summary

Malicious bidder can block any other bidder overtaking him because the protocol is sending the ETH back to him in the same transaction/function when setting the new highest bidder. 

## Vulnerability Detail

A malicious bidder, implemented as a smart contract, bids and has the highest offer. When a new bidder would overtake him, his deposit would be returned to him:
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L164-L167

while also noting, that in the same function call (`bid`), the new highest bidder is set
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L156-L157

Using a [receive/fallback](https://docs.soliditylang.org/en/v0.8.17/contracts.html#special-functions) mechanism, the malicious smart contract can be set to revert when receiving the ETH. This effectively blocks any other entity from becoming the highest bidder because the transaction would always revert.

This issues is generally resolved by `favoring pull over push for external calls`

## Impact

An attacker can enter an auction and always win by bidding just once.

## Code Snippet

Issue
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L164-L167

## Tool used

Manual Review

## Recommendation

Implement the _pull over push for external calls_ idiom; save the list of addresses to refund and have them, call the refund function in order to receive their ETH back, do not send it directly.

ConsenSys has also a good example on this which may help:

https://consensys.github.io/smart-contract-best-practices/development-recommendations/general/external-calls/#favor-pull-over-push-for-external-calls
