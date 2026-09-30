# [M] Bypass cap per address restriction

## Summary
Severity: Medium
Reporter: cat
Source: https://github.com/sherlock-audit/2023-07-beam-auction-Oot2k/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Bypass cap per address restriction

## Summary

By creating a contract that deploys new contracts, it is possible to bypass the CAP_PER_ADDRESS restriction of the MeritDutchAuction's mint() function. These newly deployed contracts have the capability to mint tokens and send them to a single wallet, all within a single transaction.

## Vulnerability Detail

The MeritDuchAuction has a cap on how many nfts a single address can mint. This function should prevent one user from buying to many nfts from one auction.

This can of course be bypassed by just creating a lot of ETH addresses, and calling mint from each one of them.   
This is migrated through frontrunning, where in a scenario where an nft is really desired, users can front run each other, which still allows a fair Competition.

Different to this, a malicious user can create a smart contract that deploys new contracts inside of a for loop, which call mint again and transfer minted NFTs in constructor back to the deployer contract. 

From my understanding the cap per address is exactly to prevent this type of behavior.

## Impact

This operation is very expensive in terms of transaction fees, 
so it allows users to mint only 2-3 times the maximum limit per address. 

Because the mintcap is low, we can assume NFTs have high value, exploiting this can be highly profitable.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction-Oot2k/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
https://github.com/sherlock-audit/2023-07-beam-auction-Oot2k/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12

## Tool used

Manual Review

## Recommendation

Based on the project description, it appears that this product is primarily designed for end users and does not involve integration with smart contracts. In this case, we can utilize the tx.origin feature to prevent a situation where one user unfairly mints an excessive number of NFTs in a single transaction.
