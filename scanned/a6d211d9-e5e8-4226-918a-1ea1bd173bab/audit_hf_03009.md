# [M] Malicious pausing the contract

## Summary
Severity: Medium
Contest weight: 0.4697
Dataset id: 16805
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Auction.sol#L204](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/auction/Auction.sol#L204)  
[Auction.sol#L206](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/auction/Auction.sol#L206)  
[Auction.sol#L235](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/auction/Auction.sol#L235)  

There is a function `_createAuction` in `Auction` contract.

It consists of the following logic:

```solidity
/// @dev Creates an auction for the next token
function _createAuction() private {
    // Get the next token available for bidding
    try token.mint() returns (uint256 tokenId) {
        **creating of the auction for token with id equal to tokenId**

        // Pause the contract if token minting failed
    } catch Error(string memory) {
        _pause();
    }
}
```

According to the [EIP-150](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md) `call` opcode can consume as most `63/64` of parrent calls’ gas. That means `token.mint()` can fail since there will be no gas.

All in all, if `token.mint()` fail on gas and the rest gas is enough for pausing the contract by calling `_pause` in `catch` statement the contract will be paused.

Please note, that a bug can be exploitable if the token.mint() consume more than 1.500.000 of gas, because 1.500.000 / 64 > 20.000 that need to pause the contract. Also, the logic of `token.mint()` includes traversing the array up to 100 times, that’s heavy enough to reach 1.500.000 gas limit.

## Recommendation
Add a special check for upper bound of `gasLeft` at start of `_createAuction` function.

Honestly I’m really impressed by the submission, however I think the quote:

`Please note, that a bug can be exploitable if the token.mint() consume more than 1.500.000 of gas, because 1.500.000 / 64 > 20.000 that need to pause the contract. Also, the logic of token.mint() includes traversing the array up to 100 times, that's heavy enough to reach 1.500.000 gas limit.`  
shows that the likelihood of this happening is extremely small, the base mint will cost between 20k and 40k gas, and each instance of the loop should roughly cost 5k, with the minting instance costing around 5k + up to 50k

From basic napkin math this is actually surprisingly possible  
![Screenshot 2022-09-20 at 00 56 54](https://user-images.githubusercontent.com/13383782/191133542-1a17c58b-2cf1-4eb4-a0c8-36b5546aa62c.png)

However I believe the odds of this happening are extremely low as you’d need to have at least 20 tokens being minted to founders  
![Screenshot 2022-09-20 at 00 58 15](https://user-images.githubusercontent.com/13383782/191133675-9b226a11-b391-4d7a-a9a6-beaed8cd88b3.png)

I think Med is more appropriate for now, I really like the catch of the OOG exploit, however I may have to downgrade further as the worst case scenario being pausing is not impactful.

I believe the finding to be valid and Medium Severity as the conditions are non-trivial, but the impact is Denial of Service which can be triggered predictably given the circumnstances.
