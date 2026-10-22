# [M] [M] Non-settleable auction can be started by owner, resulting in the winner's fund being frozen

## Summary
Severity: Medium
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L206
Type: audit-issue

## Details
# [M] Non-settleable auction can be started by owner, resulting in the winner's fund being frozen

## Summary

The auction contract contains a potential vulnerability that may allow the contract owner to start an auction for a previously sold NFT, which can lead to incorrect behavior and loss of funds.

## Vulnerability Detail

When the `max_token_id` is set and `current_epoch_token_id` equals `max_token_id`, it is possible to start a new auction for the same NFT by calling the `start_auction` function by the owner. 

when `settle` is called for the previous auction, as the `current_epoch_token_id` has not been updated to reflect the fact that the NFT has already been sold. 

As a result, if someone win the new auction, contract will not be able to correctly handle settling the auction, since the `current_epoch_token_id` already mint by last auction.

### POC

Given:

* `max_token_id` = 10
* `current_epoch_token_id` = 10
* current auction settled
* self.epoch_start = 0
* self.epoch_end = 0

1. contract owner call `start_auction`, a new auction will begin, `current_epoch_token_id` = 10

2. Alice places a bid and wins the auction

3. Alice call `settle`, contract will attempt to mint an already existing NFT, resulting in a failed transaction.

## Impact

The impact of this vulnerability could result in a loss of funds or NFTs. If the contract owner starts a new auction for a previously sold NFT without proper checks, a bidder may make a bid during the new auction. This can cause the smart contract to fail to correctly handle settling the auction, as it will be attempting to mint an NFT with an ID that has already been minted.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L206

```vyper=199
 # set up next round if there is one
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0
```

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L216-L242

```vyper=216
@external
def start_auction(_start_time: uint256):
    """
    @notice
        Sets the timestamp when the first auction starts.
        Can be changed while the auction has not started yet.
        Can only be called by current owner.
    @param _start_time
        The timestamp when the first epoch starts.
        If 0 is passed, it will start the auction now.
    """
    assert msg.sender == self.owner, "unauthorized"
    # epoch_start has already been set and is in the past
    if self.epoch_start != 0 and self.epoch_start <= block.timestamp: 
        raise "auction already started"

    start: uint256 = _start_time
    if start == 0:
        start = block.timestamp

    assert start >= block.timestamp, "cannot start in the past"

    self.epoch_start = start
    self.epoch_end = self.epoch_start + EPOCH_LENGTH

    log AuctionStart(self.epoch_start, msg.sender)
    log Bid(0, msg.sender, 123)
```
## Tool used

Manual Review / ChatGPT PLUS

## Recommendation

To mitigate this issue, it is recommended to update the start_auction function to check if current_epoch_token_id equals max_token_id before attempting to create a new auction. If it does, the function should revert and not allow the creation of a new auction until max_token_id are updated.
