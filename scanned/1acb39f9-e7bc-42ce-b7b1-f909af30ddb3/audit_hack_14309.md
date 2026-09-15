# [M] The maximum amount of NFTs that can be minted per address can be easily bypassed

## Summary
Severity: Medium
Reporter: qbs
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# The maximum amount of NFTs that can be minted per address can be easily bypassed

## Summary
Every user can bypass this minting limit by deploying multiple contracts and each of them would mint tokens within the mentioned threshold in a single transaction. 
## Vulnerability Detail
The contract allows users to mint only 4 NFTs per address. However, users can bypass this limitation by writing a contract that deploys multiple contracts, with capable of minting 4 tokens and sending them to arbitrary addresses in a single transaction.
It should be noted that users can still bypass this limit by creating multiple EAOs.
## Impact

## Code Snippet
[MeritDutchAction.sol#L143](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143)
```solidity
// Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```
## Tool used

Manual Review

## Recommendation
Consider adding the following require statement:
```solidity
require(msg.sender == tx.origin)
```
