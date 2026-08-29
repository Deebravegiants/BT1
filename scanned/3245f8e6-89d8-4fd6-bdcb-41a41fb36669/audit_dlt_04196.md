# [H] Infinite approve potentially lead to leftover fund loss

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/72
Type: sherlock-finding

## Details
__141345__

high

# Infinite approve potentially lead to leftover fund loss

## Summary

There is no check for the calldata sent to `swapTarget` contract. So the input `fromTokenAmount` for `externalSwap()` might be different from the actual amount in the external call. This difference together with the infinite approve could be abused to steal fund from the DODORouteProxy contract.


## Vulnerability Detail

When there is excess fund left in the contract, the malicious user could do the following to steal these fund:
1. input `fromTokenAmount` just enough to set the infinite approval for `fromToken`.
2. use 1inch as the external swapTarget, the input amount in `callDataConcat` will be the sum of `fromTokenAmount` and the fund balance of `fromToken` in route proxy contract.

In 1inch `swap()` function, the amount of `fromToken` transferred will be all the balance the contract holds (leftover + `fromTokenAmount`). And receive in the form of another token.

Further more, the infinite approval is forever, once the allowance is set, currently there is no way to set it back. Anytime in the future, when this kind of opportunity comes again, this vector can be used over and over.


#### token leftover

Although it seems the route proxy contract is not expected to hold tokens, there are still several possibilities that funds could stay:
- The `externalSwap()` call other contract to perform the swap, sometimes when swap for exact amount of `toToken`, more than enough `fromToken` could be sent, result in some leftover. 
- There could be tokens mistakenly sent to the contract, although it it not expected. 
- Some airdropped tokens due to multiple transactions in history, making the contract eligible for the airdrop.
- other unexpected leftovers.

In multiple chains, the DODO route address have some leftover tokens:
- ETH mainnet: https://etherscan.io/address/0xa2398842F37465f89540430bDC00219fA9E4D28a
- Polygon: 
https://polygonscan.com/address/0x2fA4334cfD7c56a0E7Ca02BD81455205FcBDc5E9
- BSC: https://bscscan.com/address/0x6B3D817814eABc984d51896b1015C0b89E9737Ca#code

And many DEX indeed have leftovers, it is a common issue. Although many are dust amounts, this issue persist, and possibly lose large amount by mistake, or dusts could accumulate into big amount. And in the contract there is a `superWithdraw()` function in case of this problem.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/72_
