# [M] TWAP price can be manipulated

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L213
Type: audit-issue

## Details
# TWAP price can be manipulated

## Summary

The protocol uses the TWAP price when calculating the minimum swap slippage protection, but the TWAP price can be manipulated.

## Vulnerability Detail

```vyper
@view
@internal
def _calc_min_amount_out(
    _amount_in: uint256, 
    _path: DynArray[address, 3], 
    _fees: DynArray[uint24, 2], 
    _twap_length: uint32, 
    _max_slippage: uint256
    ) -> uint256:

    uni_fees_total: uint256 = 0
    for fee in _fees:
        uni_fees_total += convert(fee, uint256)

    token_in_decimals: uint256 = convert(ERC20Detailed(_path[0]).decimals(), uint256)
    twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)

    min_amount_out: uint256 = _amount_in * PRECISISON 
    min_amount_out = min_amount_out * twap_value
    min_amount_out = (min_amount_out * (FEE_BASE - uni_fees_total - _max_slippage)) / FEE_BASE
    min_amount_out = min_amount_out / 10**token_in_decimals
    min_amount_out = min_amount_out / PRECISISON

    return min_amount_out
```

The TWAP price can be manipulated, which causes the calculated minAmount to be inaccurate, resulting in the user being attacked by the sandwich.

## Impact

TWAP price can be manipulated causing the slippage protection is invalid and user swap can be sandwitched.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L213

## Tool used

Manual Review

## Recommendation

Use oracle to compare price difference
