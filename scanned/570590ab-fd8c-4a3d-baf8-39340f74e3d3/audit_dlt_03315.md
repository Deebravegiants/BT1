# [M] Monopolization of the bidding platform

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-realitycards
Published: 2021-08-24
Source: https://github.com/code-423n4/2021-08-realitycards-findings/issues/31
Type: code-finding

## Details
# Handle

animixar


# Vulnerability details

## Impact
This is potentially a low-to-medium risk vulnerability as this will lead to the platform being monopolized by a handful of people; preventing any adoption and growth.


## Proof of Concept
A very few super-users with a lot of funds at their disposal can make the game inaccessible for the average player (the larger proportion) in no less than a few minutes after the start of every individual market.

For example, let's take a 24-hour long binary market. Three users with 10K at their disposal can solely compete with just each other in the first few minutes of the 24hr market to pump the rental price to an average of ~200 USDC/hour/card for the entire duration of the market. For an average user, this will be unaffordable and prevent their participation. The majority of the platform users will hence be lost due to the current design of the game.

The solution would be to make the # of maximum bids per user limited by time using "cool down" timers as discussed in the "Recommended Mitigation Steps." This will not only solve the monopolization issue but also aid to solve the issues with zero length bids and healthy price discovery.


## Tools Used
Using the RC beta thoroughly and carrying out dry runs of the relevant functions in the contract.


## Recommended Mitigation Steps
Every event in the game can come with a set number of maximum available bids per user. Let's say: 6 max. bids per user for a 24 hours market, 42 max. bids per user for a 7 days long market and so on. The # of available bids would not be an absolute number but in turn be time dependent. This can be implemented using a "cool down" timer. Every new bid placed by a user would trigger a "cool down" timer. Based on this timer, the user cannot place a new bid on the same card until the timer hits the cool down period. In the above discussed cases, the cool down period is 4 hours after every single bid. The cool down timers itself can be of different durations for say a long market vs. lightning market.

Advantages of this system which implements a "cool down" timer in the rental process would be:
- On an average, a lot more users would participate in at least the first 25% of the market duration when the rental will more likely be lower as whales don't get unlimited attempts to pump the price.
- With # of bids as a scarce in-game asset, it automatically improves the price discovery even without the hardcoded 10% rental appreciation.
- Unique gamification of the platform by adding a cool "cool down" aspect to the bids.
- Better prevention of zero length bids using multiple accounts.
