# [H] Anyone can force auction to start and the first auction to end with no winning bid

## Summary
Severity: High
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L213
Type: audit-issue

## Details
0xlmanini

false

# Anyone can force auction to start and the first auction to end with no winning bid

## Summary
When AuctionHouse#start_auction(uint256) is called with a non-zero, valid parameter, any external actor can force the auction to start before the intended time and make the first auction end with no winning bid, causing the first auctioned NFT to be sent to FALLBACK_RECEIVER

## Vulnerability Detail
Issue found at: AuctionHouse.vy#settle() and AuctionHouse.vy#start_auction(uint256)
Calling AuctionHouse#start_auction(uint256) with a valid, future timestamp allows an attacker to call AuctionHouse.vy#settle(), bypassing the initial assert statement as AuctionHouse.vy#_epoch_in_progress() returns false. 
As a consequence, winner is set to the zero address as no bid can have occurred at this point, which later results in winner being set to FALLBACK_RECEIVER.
Further down the execution of settle(), assuming max_token_id > 0, epoch_start will be set to block.timestamp, even if it is less than the value set by the previous call to AuctionHouse#start_auction(uint256), forcing the auctions to start at the current time.
Finally, the NFT with token_id = 0 will be minted to FALLBACK_RECEIVER. 
 
## Impact
Loss of first NFT of an auction, early start of auction

## Code Snippet

[settle()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L213)
[start_auction()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L217-L242)

I've also added the following test to `test_AuctionHouse_settle.py` to verify my finding

``` python

def test_settle_sends_first_nft_to_fallback_receiver_when_non_zero_start_time(house, alice, nft):
    timestamp = boa.env.vm.patch.timestamp
    start = timestamp + 10 * 60
    house.start_auction(start) # set start at some time in the future

    with boa.env.prank(alice):
       house.settle() # alice calls settle() now
    
    ### verify bug effects

    # first nft is minted to FALLBACK_RECEIVER
    assert nft.ownerOf(0) == house.FALLBACK_RECEIVER()
    # auction is started prematurely
    assert house.epoch_start() == timestamp # this implies epoch_start <= timestamp and timestamp <= epoch_end
```


## Tool used

Manual Review

## Recommendation

Change AuctionHouse.vy#settle() first assertion to assert block.timestamp > self.epoch_end
