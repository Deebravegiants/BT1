# [H] A possible reentrancy while using low level .call to refund the excess ETH to the user.

## Summary
Severity: High
Reporter: Kirkeelee
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# A possible reentrancy while using low level .call to refund the excess ETH to the user.

## Summary
MeritDutchAuction.sol refunds users who've sent excess ETH by a low-level function that can be vulnerable to reentrancy attacks. The function does not have a reentrancy guard and it makes it vulnerable.

## Vulnerability Detail
A reentrancy attack occurs when an external contract calls back into the original contract before the state is updated, allowing it to withdraw more ETH than intended. 

## Impact
Attacker can drain the ETH in the contract by repeating the call several times.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation
Use reentrancy guard, or use the checks-effects-interactions pattern to update the state before sending ETH.
