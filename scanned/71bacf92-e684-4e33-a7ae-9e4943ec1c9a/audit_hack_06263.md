# [M] Restart auction once max token is settled

## Summary
Severity: Medium
Reporter: HonorLt
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L204-L206
Type: audit-issue

## Details
# Restart auction once max token is settled

## Summary

The protocol resets epoch data once the max token id is settled making it possible to start it again.

## Vulnerability Detail

When the final token id is reached, `settle` no longer increments `current_epoch_token_id` but just resets `epoch_start` and `epoch_end`:
```vyper
    # set up next round if there is one
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0
```

Resetting this state makes it possible again for the owner to start the auction:
```vyper
    # epoch_start has already been set and is in the past
    if self.epoch_start != 0 and self.epoch_start <= block.timestamp: 
        raise "auction already started"
```

However, starting again does not make sense, because these NFTs have already been minted out.

## Impact

An owner can restart the auction once it reaches the final token it. The renewed auction can accept bids but fail to settle leaving the only option to `refund_highest_bidder`.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L204-L206

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L229-L230

## Tool used

Manual Review

## Recommendation

Maybe there is no need to nullify  `epoch_start` and `epoch_end` there. I do not see real harm if you remove this else block.
