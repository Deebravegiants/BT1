# [H] Dca.vy: Stealing User Funds Provided for DCA by Creating a New Pool and Manipulating Price

## Summary
Severity: High
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268
Type: audit-issue

## Details
# Dca.vy: Stealing User Funds Provided for DCA by Creating a New Pool and Manipulating Price

## Summary
In `execute_dca_order` function of `Dca.vy` contract which allows users to exploit DCA trades by creating custom tokens, manipulating pool prices, and consequently, draining user funds.

## Vulnerability Detail
The `execute_dca_order` function enables the execution of DCA trades. It uses the Uniswap pool's TWAP price calculated by the `_calc_min_amount_out` function to ensure that trades are conducted at an appropriate price.

Users can specify a trading path of up to three lengths. An attacker can exploit this by creating custom tokens, manipulating pool prices, and consequently draining funds intended for DCA trades.

The `_calc_min_amount_out` function serves as a sort of slippage control, but since users can define the trade path, an attacker can set this value to 0 and drain user funds. If the result of `getTwap` is 0, `_calc_min_amount_out` is calculated as 0.

```vyper
twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)
```

The vulnerability occurs when getSqrtTwapX96 from Univ3Twap.sol returns a value so large that it results in zero for the TWAP. This behavior can be observed on the Arbitrum mainnet.

An exploitation scenario could look like this:

1. User A places a DCA order to buy a certain amount of WBTC with USDT every day.
2. The attacker deploys token B, creates a `USDT-token B` pair, and sets the value of token B to be extremely high.
3. The attacker creates a `token B-WBTC` pool and sets the value of token B to be extremely low.
4. The attacker executes the DCA order with the path set to [USDT, token B, WBTC].
5. min_amount_out is set to 0, and User A receives almost no WBTC.
6. The attacker withdraws from the LP, draining User A's funds.
7. 
## Impact
The exploit can lead to substantial financial loss for users who engage in DCA trades as they could lose their funds to attackers who manipulate token prices.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L55
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41-L49
## Tool used

Manual Review

## Recommendation
To prevent such exploitation, it is recommended to adopt an external price feed, such as Chainlink oracle, when calculating `min_amount_out`. This ensures that the trades are based on accurate and trusted price data that is less susceptible to manipulation.
