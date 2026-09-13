# [M] theft of system profit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-11-malt
Published: 2021-11-27
Source: https://github.com/code-423n4/2021-11-malt-findings/issues/56
Type: code-finding

## Details
# Handle

danb


# Vulnerability details

## Impact
System profit comes from the stabilize function when the price of malt is above 1. Therefore it should not be allowed for anyone to take a part of the system profit when the price is above one. Right now, anyone can take a part of the investors' profits, even if they don't own any malt at all.
## Proof of Concept
suppose that the price went up to 1.2 dai; the investors should get the reward for this rise. instead, anyone can take a part of the reward in the following steps:
The price of malt is now 1.2 dai.
Take a flash loan of a large amount of malt.
Sell the malt for dai.
Now the price went down to 1.1 dai because of the enormous swap.
Call stabilize in order to lower the price to 1 dai.
Buy malt to repay the flash loan at a lower cost with the bought dai.
Repay the flash loan, and take the profit.

It is a sandwich attack because they sold malt for a high price, then they called stabilize to lower the value, then repurchase it for a low price.

The user made a profit at the expense of the investors.

If a user already has malt, it’s even easier:
just sell all malt at a high cost.

## Tools Used
manual review.
## Recommended Mitigation Steps
in _beforeTokenTransfer, if the price is above 1$ and the receiver is the AMM pool, stabilize it.
