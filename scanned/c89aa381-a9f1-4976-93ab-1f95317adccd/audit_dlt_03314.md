# [M] Insufficient checks at the smart contract level to ensure that previous user address is the lowest bid that is higher than the bid to be added.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-realitycards
Published: 2021-08-24
Source: https://github.com/code-423n4/2021-08-realitycards-findings/issues/37
Type: code-finding

## Details
# Handle

0xImpostor


# Vulnerability details

## Impact

I understand that it is

> Thus, it is up to the frontend to keep track of the orderbook and sort it appropriately.

however should there be a custom UI made for these contracts and it is not sorted correctly, some of the logic in the code will break.

## Proof of Concept

Instead of relying on the official UI, I'm using a community made UI but this UI doesn't maintain the sorting of the orderbook.

When I `addBidToOrderbook` is called, the `_prevUserAddress` that is passed into the function may not necessarily be the lowest bid that is higher than the bid to be added.

For example, the correct sorted order (ignoring the Minimum bid increase percentage) should be

`market, 10, 9, 7, 5, 3, 1` for a particular card. I want to make a bid of price = 4 so the correct `_prevUserAddress` should be 5 however if the address corresponding to the user who bid 9 is passed into the function so when `_requiredPrice` within `_searchOrderbook` is calculated, it is using the value of 7 to calculate the required price instead of 3. This means that no matter how many iterations are made, you will never be able to find a position in the orderbook. 

## Tools Used

Manual analysis

## Recommended Mitigation Steps

There is no quick fix for this and requires quite a substantial revamp of the design. A naive band solution would be to iterate through the linked lists but this is a bad solution.
