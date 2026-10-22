# [H] User Loss Money When Failed Bid Creation During `createBid` Process

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-09
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/37
Type: hats-finding

## Details
**Github username:** @kevinkien
**Submission hash (on-chain):** 0x2b98a4379cdfa4ccdeb6c422246b2bd0ddc70b0b739831945806b78e922a894e
**Severity:** high

**Description:**
**Description**

When users initiate the creation of a bid with a certain amount of ether. Upon performing the condition check within the code segment:

```
if (whitelistEnabled) {
            require(
                nodeOperatorManager.isWhitelisted(msg.sender),
                "Only whitelisted addresses"
            );
            require(
                msg.value == _bidSize * _bidAmountPerBid &&
                    _bidAmountPerBid >= whitelistBidAmount &&
                    _bidAmountPerBid <= maxBidAmount,
                "Incorrect bid value"
            );
        } else {
            if (
                nodeOperatorManager.isWhitelisted(msg.sender)
            ) {
                require(
                    msg.value == _bidSize * _bidAmountPerBid &&
                        _bidAmountPerBid >= whitelistBidAmount &&
                        _bidAmountPerBid <= maxBidAmount,
                    "Incorrect bid value"
                );
            } else {
                require(
                    msg.value == _bidSize * _bidAmountPerBid &&
                        _bidAmountPerBid >= minBidAmount &&
                        _bidAmountPerBid <= maxBidAmount,
                    "Incorrect bid value"
                );
            }
        }
```

If the conditions within the `require` statement are not met, the function will halt and not refund the money to the bid creator.

**Attack Scenario**

The user creates a bid with an incorrect amount of money (msg.value) when checking the conditions within the `require` statement. When the condition is incorrect, the user will lose the money.

**Attachments**

1. **Proof of Concept (PoC) File**

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/AuctionManager.sol#L100-L160

2. **Revised Code File (Optional)**

Add a code to refund the money to the bid creator if failed bid creation.

```
(bool success, ) = payable(msg.sender).call{value: msg.value}("");
require(success, "Unsuccessful money transfer.");
```
