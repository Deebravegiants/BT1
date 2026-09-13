# [M] Missing check allows zero-amount minting

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# Missing check allows zero-amount minting

## Summary

There is a bug in the `mint` function of the provided smart contract code. It allows users to mint with an amount of `0`, which can create a loophole for malicious actors and potentially interfere with offchain integrations.

## Vulnerability Detail

The issue lies in the absence of a check to ensure that the `amount` argument of the `MeritDutchAuction.mint` function is greater than 0. Without this check, it's possible to call the function with an `amount` of 0. This might cause issues in any off-chain systems listening to the `Minted` event, as it doesn't enforce any amount to be minted.

## Impact

The impact of this bug can range from minor to severe, depending on how offchain systems are using the `Minted` event. For instance, a bug like this can be used to cause Denial of Service (DoS) by emitting an overwhelming number of `Minted` events, effectively clogging the offchain systems with unnecessary data. Additionally, this might create inconsistencies between on-chain and off-chain data.

## Code Snippet

[MeritDutchAuction.sol#L128](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128)
```solidity
function mint(uint256 amount) external payable {
    // @audit missing require, amount > 0 this will let bad actor bypass the mint, and emit a "MINTED" event without having mint
    // Checks
    // ...
    // Make sure enough ETH was sent in the transaction
    require(msg.value >= totalPaid, "Insufficient funds");

    // ...
    // Emit event for offchain integrations
    emit Minted(msg.sender, amount, pricePaid);
}
```

This is a small poc:
```solidity
 function testMintZeroAmount() public {
        vm.startPrank(wallet1);
        vm.warp(startTime);
        auction.mint{value: START_PRICE}(0);
 }
```


## Tool used

Manual Review

## Recommendation

Adding a simple requirement check for the `amount` to be greater than zero should resolve this issue. The updated code would look something like this:

```solidity
function mint(uint256 amount) external payable {
    require(amount > 0, "Amount must be greater than 0");

    // ... remaining code ...
}
```

This way, we ensure that an `amount` of 0 cannot bypass the mint process and cause issues with the `Minted` event.
