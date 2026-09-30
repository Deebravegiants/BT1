# [M] The `Furnace#melt`

## Summary
Severity: Medium
Contest weight: 0.3651
Dataset id: 18092
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can get more of the RToken appreciation benefit brought by `Furnace.sol#melt()`(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/Furnace.sol#L70), and long-term RToken holders will get less benefit.

RToken holders will be less willing to provide liquidity to RToken pools (such as uniswap pools), resulting in less liquidity of RToken.

## Proof of Concept
**A1. Gain revenue from a flashloan sandwich attack**

A malicious user can launch a flashloan sandwich attack against `Furnace#melt()`(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/Furnace.sol#L70) each time a whole period passed (payout happens).

The attack transaction execution steps:

  1. Borrow some assets (`inputFund`) with a flashloan
  2. Swap the `inputFund` for RToken
  3. Call `RToken#redeem()`(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/RToken.sol#L439) to change the RToken to basket assets(`outputFund`). The `redeem()` will invoke `Furnace.melt()` automatically.
  4. Swap part of `outputFund` for `inputFund` and pay back the flashloan, the rest of `outputFund` is the profit.

The implicit assumption here is that most of the time the prices of RToken in `RToken.issues()`, `RToken.redeem()`, and DeFi pools are almost equal.

This assumption is reasonable because if there are price differentials, they can be balanced by arbitrage.

The attack can be profitable for:

  * `Furnace#melt()` will increase the price of RToken in issue/redeem (according to basket rate).
  * Step 2 buys RTokens at a lower price, and then step 3 sells RTokens at a higher price(`melt()` is called first in `redeem()`).

**A2. Get a higher yield by holding RToken for a short period of time**

Malicious users can get higher yield by by following these steps:

  1. Calculate the next payout block of Furnace in advance
  2. Call `RToken#issue()`(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/RToken.sol#L177) 1 to n blocks before the payout block
  3. Call `RToken#redeem()`(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/RToken.sol#L439) when the payout block reaches.

Since this approach only requires 1 to n blocks to issue in advance, which is typically much smaller than rewardPeriod, the attacker will obtain much higher APR than long-term RToken holders.

## Recommendation
Referring to eip-4626(https://eips.ethereum.org/EIPS/eip-4626), distribute rewards based on time weighted shares.

Alternatively, always use a very small rewardPeriod and rewardRatio, and lower the upper limit MAX _RATIO and MAX_ PERIOD(https://github.com/reserve-protocol/protocol/blob/df7ecadc2bae74244ace5e8b39e94bc992903158/contracts/p1/Furnace.sol#L15-L16).

Agreed with the warden. And agree this is a Medium severity issue.

(aside: we are already planning to fix the period at 12s to mitigate this issue)

Addressed here: https://github.com/reserve-protocol/protocol/pull/571
