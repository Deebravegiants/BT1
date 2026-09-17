# [M] Missing transaction deadline in `MeritDutchAuction.mint` Function

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# Missing transaction deadline in `MeritDutchAuction.mint` Function

## Summary

There is a missing deadline in the `MeritDutchAuction.mint` function that poses a potential vulnerability to users. If a user sends more ETH than necessary, and the price subsequently changes drastically, the user could end up overpaying.

## Vulnerability Detail

The current `mint` function does not set a deadline for transactions, meaning that the price of NFTs could change before a transaction is completed. This makes the function susceptible to potential price manipulation or drastic price changes during the transaction window. If a user sends more ETH than necessary and the price changes, they would lose the extra ETH they sent in.

## Impact

This issue could potentially lead to the loss of users' funds. Users could lose extra ETH they sent in if the price changes drastically before a transaction completes.

## Code Snippet

[MeritDutchAuction.sol#L128](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128)
```solidity
function mint(uint256 amount) external payable {
    // Price being paid is the current price
    uint256 pricePaid = getPrice();
    // Total price being paid is the current price times the amount of NFTs
    uint256 totalPaid = pricePaid * amount;
    ...
    if(msg.value > totalPaid) {
        // If too much ETH was sent, refund the difference
        (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
        require(success, "Refund failed");
    }
    ...
}
```

## Tool used

Manual Review

## Recommendation

To mitigate this issue, a deadline should be set for each transaction to prevent users from being affected by price changes during the transaction window. If the transaction does not complete before the deadline, it should be canceled and all ETH should be returned to the user. This will ensure that users are only paying the price they agreed to when initiating the transaction.

Here's an example of how to implement a transaction deadline:

```solidity
function mint(uint256 amount, uint256 deadline) external payable {
    require(block.timestamp <= deadline, "Transaction expired");
    ...
}
```

The `deadline` parameter can be passed into the `mint` function, and the user can set this when they call the function. If the current timestamp is greater than the `deadline`, the transaction will fail with the message "Transaction expired".
