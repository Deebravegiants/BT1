# [H] Address limit can be bypassed using a contract

## Summary
Severity: High
Reporter: neumo
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159
Type: audit-issue

## Details
# Address limit can be bypassed using a contract

## Summary
The auction contract is designed to disallow users from minting more than `CAP_PER_ADDRESS` NFTs per acount. This can easily be bypassed using a smart contract.

## Vulnerability Detail
As we have seen in the past, this kind of protection to prevent a single person to own a big amount of assets simply don't work. The Adidas NFT of December 2021 is a good example, where there was a cap of 2 NFTs per account, the sale lasted just 10 seconds, and a single user was able to mint 330 NFTs:
https://nftevening.com/someone-sidestepped-adidas-nft-minting-terms-to-score-330-nfts/

The idea to bypass the limit in a single transaction is to use a smart contract that executes a loop, inside of which it deploys a simple contract that mints `CAP_PER_ADDRESS` NFTs in the `MeritDutchAuction` contract and sends them to the attacker. The limit here is just the gas, the attacker will have to make the loop short enough to not surpass the block gas limit.


## Impact
High.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159

## Tool used
Manual review.


## Recommendation
Add this constraint to the `mint` function:

```solidity
require(tx.origin == msg.sender)
```

This will ensure that the caller is an EOA and not a smart contract.
