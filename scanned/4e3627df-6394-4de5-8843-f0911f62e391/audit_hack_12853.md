# [H] DCA order value can be stolen in entirety

## Summary
Severity: High
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268-L274
Type: audit-issue

## Details
# DCA order value can be stolen in entirety

## Summary
Anyone can execute a pending DCA order by calling `Dca.execute_dca_order()`. The caller provides the path and Uniswap fees to determine which UniV3 pools the tokens are exchanged from/to.

This open approach can allow an attacker to steal all value from a DCA order. The attacker will perform the following steps:

- Create their own ERC20 ($STEAL)
- Deploy multiple STEAL/token pools
- Provide minimal liquidity to these pools
- Execute Unstoppable DCA orders and route them through these pools

Since `Dca._calc_min_amount_out()` relies on the pool's TWAP value for the `min_amount_out` and the TWAP value of the pool is controlled by the attacker, the attacker can make this nearly **0**.

## Vulnerability Detail
An attacker can execute a DCA order with an arbitrary 3-token path:
`WETH -> STEAL -> USDC`

Therefore, an attacker will create both `STEAL/WETH` and `STEAL/USDC` pools with whichever fee amount desired. It really doesn't matter because only the attacker owns STEAL. These pools will contain unfavorable exchange rates between the tokens.

The pool's TWAP values will be low (nearly 0), which the call to `Dca._calc_min_amount_out()` will read as the truth.

```solidity
    twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)

    min_amount_out: uint256 = _amount_in * PRECISISON 
    min_amount_out = min_amount_out * twap_value
    min_amount_out = (min_amount_out * (FEE_BASE - uni_fees_total - _max_slippage)) / FEE_BASE
    min_amount_out = min_amount_out / 10**token_in_decimals
    min_amount_out = min_amount_out / PRECISISON
```

The `twap_value` is calculated by calling `TWAP.getTwap()` which reads the observations from the pool. The returned TWAP value is completely controlled by the attacker who is the only account that owns STEAL and can provide liquidity. Also, STEAL would also have logic in its `_transfer()` that only allows it to be transferred to specific places to ensure that full TWAP control can be achieved.

## Impact
- Theft of all DCA orders

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268-L274

## Tool used
Manual Review

## Recommendation
Contain a whitelist of approved path/fee combinations. As long as arbitrary 3-token paths are allowed, anyone can route these orders through pools with arbitrary TWAP values.
