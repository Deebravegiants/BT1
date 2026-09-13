# [M] Max token id cannot be changed once final token is settled

## Summary
Severity: Medium
Reporter: HonorLt
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L208
Type: audit-issue

## Details
# Max token id cannot be changed once final token is settled

## Summary

The protocol cannot resume auctioning new tokens if the `max_token_id` is updated after all the previous tokens minted out.

## Vulnerability Detail

The `settle` only increments `current_epoch_token_id` if it is not the final token. If it is the final token, it mints it but the id stays the same:
```vyper
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0

    MintableNFT(NFT).mint(winner, token_id)
```

However, there is a possibility that the max token id can change:
```vyper
@external
def set_max_token_id(_new_max_token_id: uint256):
    """
    @notice
        Changes the max_token_id and the amount of NFTs to be auctioned.
        Can only be called by owner.
    @param _new_max_token_id
        The last token id to be minted.
    """
    assert msg.sender == self.owner, "unauthorized"
    assert _new_max_token_id >= self.current_epoch_token_id, "cannot set max < current"

    self.max_token_id = _new_max_token_id
```

If the previous `max_token_id` was settled and then updated to a new value, it will be impossible to continue because `current_epoch_token_id` was not incremented but minted.

## Impact

The current implementation makes the updates of the max token id useless once the initial tokens mint out. 

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L199-L208

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L284-L296

## Tool used

Manual Review

## Recommendation

Consider handling the aforementioned case or documenting if this is an intended behavior.
