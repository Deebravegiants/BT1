# [H] Insufficient Funds Handling on `mint()` struct

## Summary
Severity: High
Reporter: moneyversed
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# Insufficient Funds Handling on `mint()` struct


## Summary

A security vulnerability in the `mint()` function of the `MeritDutchAuction.sol` contract could cause excess funds sent by a user to become permanently stuck in the contract.

## Vulnerability Detail

The `mint()` function allows users to mint NFTs by sending the corresponding ETH. When a user sends more ETH than the total cost, the contract attempts to refund the excess amount. However, if the refunding fails, for example, due to a failing fallback function in the calling contract, the contract operation continues as if nothing happened.

## Impact

The impact of this issue can be high in case the user sends significantly more ETH than required. The excess funds will be trapped in the contract, effectively causing a financial loss for the user.

## Code Snippet

The flaw is located in the `mint()` function:

```solidity
    if(msg.value > totalPaid) {
        // If too much ETH was sent, refund the difference
        (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
        require(success, "Refund failed");
    }
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165

## Tool used

Manual Review

## Recommendation

The contract should stop the operation and revert the transaction when the refund fails. A possible fix could be moving the `require` statement out of the `if` clause:

```solidity
    if(msg.value > totalPaid) {
        // If too much ETH was sent, refund the difference
        (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
    }
    require(success, "Refund failed");
```

## Proof Of Concept

To reproduce the issue:

1. Setup a fork of mainnet on a local blockchain network such as Ganache or Hardhat.
2. Deploy the `MeritDutchAuction.sol` contract.
3. Create a transaction from a user contract that has a failing fallback function to mint an NFT with excess funds.
4. Observe that the transaction does not fail, and the excess funds are trapped in the contract. 

Here is a mock example of a user contract with a failing fallback function:

```solidity
contract UserContract {
    MeritDutchAuction public auction;

    constructor(MeritDutchAuction _auction) {
        auction = _auction;
    }

    function buyNFT() external payable {
        auction.mint.value(msg.value)(1);
    }

    // Fallback function
    fallback() external payable {
        require(false, "Fallback failed");
    }
}
```

In the above contract, when the `buyNFT` function is called, it will result in the fallback function of `UserContract` being called, which will always fail and result in trapping the user's funds.
