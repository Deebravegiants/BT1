# [H] No NFTs can be minted after initial `max_token_id`

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L208
Type: audit-issue

## Details
# No NFTs can be minted after initial `max_token_id`

## Summary
Once the initial `max_token_id` has been reached, no NFTs can be minted even after raising the minting cap via `max_token_id`.

## Vulnerability Detail
Upon auction settlement, the round setup is as follows:
```vyper
if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
else:
    self.epoch_start = 0
    self.epoch_end = 0
```

Notice how `current_epoch_token_id` isn't incremented in the case that `current_epoch_token_id == max_token_id` (I name this the final auction). This means that the lastest NFT token id to be minted will be `max_token_id`.

There is a function that allows the minting cap to be raised: `set_max_token_id()`. However, `current_epoch_token_id` will still be equal to the previous `max_token_id` still. Hence, upon auction settlement, the NFT will attempt to mint token id `max_token_id`, which reverts because it has already been minted.

## POC
Insert this test case in `test_AuctionHouse_settle.py`.
```py
def test_settle_after_max_token_id_reached(house):
    # Step 0: Setup - Auction up to & inclusive of max_token_id
    house.start_auction(0)
    for i in range(house.current_epoch_token_id(), house.max_token_id() + 1):
        house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
        timetravel(house.epoch_end() + 1)
        house.settle()

    # Step 1: Increase `max_token_id`, start new auction
    house.set_max_token_id(house.max_token_id() + 5)
    house.start_auction(0)

    # Step 2: Bid on current auction
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    timetravel(house.epoch_end() + 1)

   # Step 3: Settlement reverts
    with boa.reverts():
        house.settle()
```

## Impact
Given that the AuctionHouse will be given ownership (only NFT owner can mint), but has no capability to transfer ownership, no migration can be performed. Hence, no new NFTs can be minted once the initial `max_token_id` has been reached.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L208

## Tool used
Manual Review

## Recommendation
At first glance, the fix might seem simple: increment `current_epoch_token_id()` in the else case too. However, this leads to another possible DoS: repeated settlement. Because `_epoch_in_progress()` will remain as `false` in the final auction, anyone can call `settle()` multiple times to repeatedly mint [`old_max_token_id`, `new_max_token_id`] to the `FALLBACK_RECEIVER`.

Incrementing in `set_max_token_id` might work, but one has to consider how to prevent repeated calls to increment `current_epoch_token_id` multiple times.

Also, prevent auction settlement if there is no auction (revert if `self.epoch_end == 0`).
