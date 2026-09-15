# [M] ERC20 transfer failure could lock user fund and cancel auction

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L227
Type: audit-issue

## Details
# ERC20 transfer failure could lock user fund and cancel auction

## Summary

Some ERC20 have pause mode, `cancelLimitOrder()`and `processAuction()` would fail. User funds could be temporarily locked, auction has to be cancelled due to the external dependance.


## Vulnerability Detail

Some ERC20 have pause mode, if toggled on, all the `transfer()` and `transferFrom()` will revert, causing the other protocols fail to function if depending on token transfer. The `cancelLimitOrder()` and `processAuction()` functions are within the affected scope, since some ERC20 (WBTC/USDC/USDT) can be paused.


### Reference

WBTC
https://etherscan.io/token/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599#code

USDC
https://etherscan.io/address/0xa2327a938febf5fec13bacfb16ae10ecbc4cbdcf#code

USDT
https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7#code


## Impact

- Users can not cancel the order and lose fund due to DoS.
- `cancelLimitOrder()` will fail, user funds could be temporarily locked.
- `withdraw()` won't work, user funds could be temporarily locked.
- `processAuction()` will fail, and the auction has to be cancelled if not processed within 24 hours of the auction end time. But this is caused by external dependance, some user could lose profit due to this failure.


## Code Snippet


`cancelLimitOrder()`:
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L227


`transferPremium()`:
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L373

`processAuction()` need to call `transferPremium()`.


## Tool used

Manual Review


## Recommendation

Provide alternative options to postpone the ERC20 transfer, just to perform the `cancelLimitOrder()` and `processAuction()` in internal records.
