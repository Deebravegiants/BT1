# [H] AuctionHouse will become bricked if it ever hits max tokenID even if max tokenID is increased later

## Summary
Severity: High
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L187-L208
Type: audit-issue

## Details
# AuctionHouse will become bricked if it ever hits max tokenID even if max tokenID is increased later

## Summary

The token accounting is AuctionHouse is flawed if current_epoch_token_id == max_token_id and it will permanently brick minting if this ever happens.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L187-L208

When AuctionHouse#settle is called it caches current_epoch_token_id and then attempts to mint that token_id. On the epoch that it reaches max_token_id, it won't increment the current_epoch_token_id. The issue with this is that once this occurs the contract will be bricked and can never mint another NFT. This is because it will attempt to double mint the original max_token_id which will always revert. Even if max_token_id is increased and the owner uses start_auction to restart the auction it will still revert.

Example:
Assume max_token_id = 10. When current_epoch_token_id == 10, settle will mint token_id = 10 but it won't increment current_token_id so that will remain at 10. Now the owner increases the cap to 15 and starts the auction. When trying to settle the auction token_id = 10 which will revert at the mint call because token_id = 10 already exists.

Submitting as high because if this contract becomes bricked, it is impossible to change the owner of the NFT (see my other submission for this issue).

## Impact

AuctionHouse will become bricked if current_epoch_token_id == max_token_id

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L213

## Tool used

Manual Review

## Recommendation

AuctionHouse#settle should always increment current_epoch_token_id even if it doesn't start a new auction:

    +   self.current_epoch_token_id += 1

        # set up next round if there is one
        if self.current_epoch_token_id < self.max_token_id:
    -       self.current_epoch_token_id += 1
            self.epoch_start = block.timestamp
            self.epoch_end = self.epoch_start + EPOCH_LENGTH
        else:
            self.epoch_start = 0
            self.epoch_end = 0
