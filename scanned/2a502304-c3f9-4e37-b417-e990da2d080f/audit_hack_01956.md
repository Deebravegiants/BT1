# [M] 6.3 ZapYCRV _min_out LPYCRV Limit

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

In ZapYCRV.zap, the _min_out argument of the zap function asserts a lower bound on the amount of
output token received by the user. When _output_token is LPYCRV it incorrectly asserts the amount of
liquidity tokens issued as an intermediate conversion step by Curve(POOL).add_liquidity.


In the LPYCRV branch of _convert_to_output, _min_out gets first passed to _lp(), which uses it
as a lower bound to the amount of liquidity tokens issued by Curve(POOL).add_liquidity()

```
@internal
def _lp(_amounts: uint256[2], _min_out: uint256, _recipient: address) -> uint256:
return Curve(POOL).add_liquidity(_amounts, _min_out)
```
It is then used again as a lower bound for amount_out issued by Vault(LPYCRV).deposit().

```
amount_out: uint256 = Vault(LPYCRV).deposit(self._lp([0, amount], _min_out, _recipient))
assert amount_out >= _min_out # dev: min out
```
This basically makes _min_out used for limit of LPYCRV vault shares and POOL LP shares. Due to
how the share values are computed, in the general case they will be not worth 1:1. Thus, _min_out as a
limit is not practical.

Code corrected

The _min_out argument of the _lp function has been removed. Thus it is not used as a lower bound to
the amount of liquidity tokens issued by Curve(POOL).add_liquidity() anymore.

```
@internal
def _lp(_amounts: uint256[2]) -> uint256:
return Curve(POOL).add_liquidity(_amounts, 0)
```
Yearn notes:

```
Hardcode the minimum to 0 in add_liquidity, as we will rely on subsequent check to
compare user inputted min_out.
```
