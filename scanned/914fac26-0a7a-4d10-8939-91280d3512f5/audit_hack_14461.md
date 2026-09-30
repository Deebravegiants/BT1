# [H] Automatic sending of excess Ether back to the sender in Mint function introduces re-entrancy attacks

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# Automatic sending of excess Ether back to the sender in Mint function introduces re-entrancy attacks

## Summary
While this mint function refunds the excess amount, it introduces a potential security vulnerability. The call function used for refunding the excess Ether performs an external call to the user's address.
## Vulnerability Detail
The refund is automatically triggered within the same transaction that mints the NFTs. This leaves the contract vulnerable to reentrancy attacks. An attacker could potentially exploit this vulnerability by deploying a malicious contract that re-enters the MeritDutchAuction contract during the refund process and performs additional undesired operations
## Impact
An attacker can  create a malicious contract that calls the mint function, and when the contract receives the excess Ether refund, it could immediately invoke a function in the attacker's contract, repeating the process and draining the contract's funds
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
## Tool used

Manual Review

## Recommendation
Use a more secure pattern, such as the "pull" method, where users explicitly withdraw their refunds instead of relying on automatic refunds in the Mint function.
