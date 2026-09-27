# [M] Malicious user can bypass Cap per address and mint the max amount in one transaction

## Summary
Severity: Medium
Reporter: shogoki
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L133
Type: audit-issue

## Details
# Malicious user can bypass Cap per address and mint the max amount in one transaction

## Summary

A malicious user can mint all NFTs invoke transaction, which bypasses the limitation to only mint 4 NFTs at once.

## Vulnerability Detail

The Dutchauction contract uses a `CAP_PER_ADDRESS`, hardcoded to 4, to prevent users from minting more than 4 NFTs. This means a user should only be able to mint 4 NFTs per transaction. However, an attacker can use a smart contract to mint all tokens in one transaction. 
The steps would be the following:
- create contract with entry point:
- Fund contract with enough eth
- Loop until the mint cap is reached
         - create a new contract with anfunction to call mint and transfer the nfts to attacker
        - fund new contract with enough eth
        - call function to mint and transfer
 This will all happen in one transaction.
As the Auction contract only checks for the msg sender address, the new created contracts will pass the cap per address check.


## Impact

User can mint all tokens in one transaction and bypass the mint per address limit

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L133

[https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L1](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L133)43

## Tool used

Manual Review

## Recommendation

- Allow mint only for EOA or whitelisted contracts.
- Maybe a check for tx.origin would be good in this case
