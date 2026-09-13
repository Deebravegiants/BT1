# [M] Auction ends can be post-poned indefinitely

## Summary
Severity: Medium
Reporter: carrot
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L160-L162
Type: audit-issue

## Details
# Auction ends can be post-poned indefinitely

## Summary
The auction contract allows a user to postpone the end of the auction by 15 minutes if they submit a bid in the last 15 minutes. This feature isn't capped and thus can be extended indefinitely.
## Vulnerability Detail
The auction contract allows a postponing of the end of the auction if a bid is submitted in the last 15 minutes
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L160-L162
The contract however does not check if it has already been postponed previously. This can lead to a user submitting a new bid every 15 minutes to postpone the auction further, delaying the auction of subsequent tokenIds.

For every new bid, the attacker must submit a bid at least 1.02 times their previous bid. To delay the auction by an entire day, they need to submit a bid with 1.02^(24*4)=6.69 times their initial bid, provided no other users have shown interest. If the bids are of low values (say 0.1 ETH), this attack vector can be likely. This will delay the subsequent auctions by an indefinite amount of time.
## Impact
Indefinitely delayed auctions
## Code Snippet
The POC below shows the auction being delayed by more than a day. The cost is less than 7.6 times the reserve price but can be even lower since 1.021 is used instead of 1.02 as the price multiplier
```python
def test_ATTACK_delay(owner, house, nft):
    token_id = house.current_epoch_token_id()
    house.start_auction(0)
    bid_amount = house.RESERVE_PRICE()
    bid_amount_init = bid_amount
    end_time = house.epoch_end()
    for i in range(96 + 1):
        timetravel(house.epoch_end() - 1)
        house.bid(token_id, bid_amount)
        bid_amount = int(float(bid_amount) * 1.021)
    assert house.epoch_end() >= end_time + 60 * 60 * 24
    assert bid_amount < float(house.RESERVE_PRICE()) * 7.6
```
## Tool used
Boa
Manual Review

## Recommendation
Only allow extension of the timeline a limited number of times
