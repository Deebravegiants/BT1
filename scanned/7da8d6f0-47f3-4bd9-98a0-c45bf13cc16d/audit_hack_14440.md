# [M] An attacker can delay the NFT Minting for Other Users by spamming txns

## Summary
Severity: Medium
Reporter: Sm4rty
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L126C1-L169C6
Type: audit-issue

## Details
# An attacker can delay the NFT Minting for Other Users by spamming txns

## Summary
The vulnerability allows an attacker to temporarily DoS to the minting process of non-fungible tokens (NFTs) by frontrunning and spamming transactions. 

## Vulnerability Detail
- The **`mint`** function allows for zero tokens to be minted.
- The **`mint`** function can be frontrun by an attacker, enabling them to execute the function before other users.

By combining these issues, an attacker can craft multiple transactions of the **`mint`** function with zero tokens as the parameter, effectively spamming the contract. As zero tokens are minted, the attacker can continuously call the function, preventing it from reaching the **`CAP_PER_ADDRESS`** limit for the attacker. Consequently, other users' transactions are delayed from interacting with the contract.

## Impact
The attacker can perform a temporary DoS attack, preventing other users from minting NFTs. This can create a negative user experience and potentially lead to financial losses for the protocol, as users who were willing to pay higher prices may end up acquiring the NFT at lower prices due to the temporary DoS.

## Proof of Concept
Consider a scenario where the contract owner starts an auction for a rare NFT with a starting price of 100 ETH and an end price of 10 ETH with a short duration. The attacker can frontrun other users with a large number of `mint(0)` transactions, and delay their NFT minting at higher prices. After some time, When the price is lowered, users will mint the NFT at a lower price and the excess price will be returned back to the users, resulting in a loss for the protocol. Users were willing to pay a higher price, but due to the temporary DoS, they obtained it later at a lower price.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L126C1-L169C6

## Tool used
Manual Review

## Recommendation
Add a `require` statement at the beginning of the mint function to check if the mint amount is greater than zero. This will prevent the function from being executed with a zero-mint amount and the attacker cannot spam the transactions.
