# [M] Missing `mint()`  Input Validation Leads to DoS Attack

## Summary
Severity: Medium
Reporter: moneyversed
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Missing `mint()`  Input Validation Leads to DoS Attack

## Summary

In the MeritDutchAuction.sol contract, the `mint` function is vulnerable to a Denial-of-Service (DoS) attack due to missing validation on the amount to be minted, which allows an attacker to exhaust the gas limit of the block, thereby preventing any other transactions from being included in the block. This type of attack, called a block stuffing attack, can effectively shut down the smart contract.

## Vulnerability Detail

In the `mint` function, the contract does not validate the input amount before entering the for loop that mints the NFTs. An attacker could provide a large amount as input and exhaust the gas limit of the block, preventing any other transactions from being included in the block. This results in a Denial-of-Service attack where legitimate users are unable to transact with the contract.

## Impact

This vulnerability allows an attacker to shut down the contract by making it impossible for other transactions to be included in the block. This would effectively prevent other users from interacting with the contract, making it unusable and potentially leading to financial loss for those unable to access their assets. 

## Code Snippet

```solidity
function mint(uint256 amount) external payable {
    ...
    for(uint256 i = 0; i < amount; i++) {
        // Mint the amount of NFTs to the sender
        nft.mint(mintedBefore + i + 1, msg.sender);
    }
    ...
}
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

To mitigate this vulnerability, it is recommended to set an upper limit to the `amount` that can be minted in a single transaction. This limit should be determined based on the amount of computation required to mint a single NFT and the current Ethereum block gas limit.

## Proof Of Concept

to reproduce such scenario:

1. Deploy the MeritDutchAuction contract with appropriate parameters.
2. Call the `mint` function with an extremely large value for the `amount` parameter, such as 2^256 - 1.
3. Observe that the transaction runs out of gas and fails, and no other transactions can be included in the same block due to the exhaustion of the block's gas limit.
