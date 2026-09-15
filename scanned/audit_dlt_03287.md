# [H] IndexPool:  Poor conversion from Balancer V1's corresponding functions

## Summary
Severity: High
Chain: Smart contract
Component: 2021-09-sushitrident
Published: 2021-09-29
Source: https://github.com/code-423n4/2021-09-sushitrident-findings/issues/40
Type: code-finding

## Details
# Handle

GreyArt


# Vulnerability details

### Impact

A number of functions suffer from the erroneous conversion of Balancer V1's implementation.

- `_compute()` (equivalent to Balancer's `[bpow()](https://github.com/balancer-labs/balancer-core/blob/master/contracts/BNum.sol#L108-L126)`)
    - `if (remain == 0) output = wholePow;` when a return statement should be used instead.
- `_computeSingleOutGivenPoolIn()` (equivalent to Balancer's `[_calcSingleOutGivenPoolIn()](https://github.com/balancer-labs/balancer-core/blob/master/contracts/BMath.sol#L195-L224)`)
    - `tokenOutRatio` should be calculated with `_compute()` instead of `_pow()`
    - `zaz` should be calculated with `_mul()` instead of the native `*`
- `_pow()` (equivalent to Balancer's `[bpowi()](https://github.com/balancer-labs/balancer-core/blob/master/contracts/BNum.sol#L89-L103)`)
    - Missing brackets `{}` for the for loop causes a different interpretation
    - `_mul` should be used instead of the native `*`

### Recommended Mitigation Steps

The fixed implementation is provided below.

```jsx
function _computeSingleOutGivenPoolIn(
  uint256 tokenOutBalance,
  uint256 tokenOutWeight,
  uint256 _totalSupply,
  uint256 _totalWeight,
  uint256 toBurn,
  uint256 _swapFee
) internal pure returns (uint256 amountOut) {
    uint256 normalizedWeight = _div(tokenOutWeight, _totalWeight);
    uint256 newPoolSupply = _totalSupply - toBurn;
    uint256 poolRatio = _div(newPoolSupply, _totalSupply);
    uint256 tokenOutRatio = _compute(poolRatio, _div(BASE, normalizedWeight));
    uint256 newBalanceOut = _mul(tokenOutRatio, tokenOutBalance);
    uint256 tokenAmountOutBeforeSwapFee = tokenOutBalance - newBalanceOut;
    uint256 zaz = _mul(BASE - normalizedWeight, _swapFee);
    amountOut = _mul(tokenAmountOutBeforeSwapFee, (BASE - zaz));
}

function _compute(uint256 base, uint256 exp) internal pure returns (uint256 output) {
  require(MIN_POW_BASE <= base && base <= MAX_POW_BASE, "INVALID_BASE");
  
  uint256 whole = (exp / BASE) * BASE;   
  uint256 remain = exp - whole;
  uint256 wholePow = _pow(base, whole / BASE);
  
  if (remain == 0) return wholePow;
  
  uint256 partialResult = _powApprox(base, remain, POW_PRECISION);
  output = _mul(wholePow, partialResult);
}

function _pow(uint256 a, uint256 n) internal pure returns (uint256 output) {
  output = n % 2 != 0 ? a : BASE;
  for (n /= 2; n != 0; n /= 2) {
		a = _mul(a, a);
    if (n % 2 != 0) output = _mul(output, a);
	}
}
```
