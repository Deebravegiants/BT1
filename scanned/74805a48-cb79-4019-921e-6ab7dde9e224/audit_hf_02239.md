# [H] Possible Price manipulation For _kalmPrice()/_getLpPrice()

## Summary
Severity: High
Contest weight: 0.5992
Dataset id: 12349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The KalmarBondingStrategy contract defines two functions (i.e., _kalmPrice() and _getLpPrice()) to obtain the prices of kalm Token and lp Token. During the analysis of these two functions, we notice the prices of kalm Token/lp Token are possible to be manipulated.
In the following, we use the _kalmPrice() routine as an example.
To elaborate, we show below the related code snippet of the KalmarBondingStrategy contract.
is derived from (otherPERkalm*_usdTokenPrice())/(10**decimalsOther) (line 236), where the value of otherPERkalm is calculated by (1e18*otherReserve)/kalmReserve. Although the price of BUSD is obtained from the chainlink and cannot be manipulated, kalmReserve or otherReserve is the token amount in trustworthy.
```solidity
function _kalmPrice() internal view returns (uint256) {
    IPancakeswapV2Pair pair = IPancakeswapV2Pair(lp);
    address other = pair.token0() == kalm ? pair.token1() : pair.token0();
    (uint256 Res0, uint256 Res1,) = pair.getReserves();
    (uint256 kalmReserve, uint256 otherReserve) = pair.token0() == kalm ? (Res0, Res1) : (Res1, Res0);
    uint256 decimalsOther = IERC20Detailed(other).decimals();
    // amount
    uint256 otherPERkalm = (1e18 * otherReserve) / kalmReserve;
    Public
    uint256 kalmPrice = (otherPERkalm * _usdTokenPrice()) / (10**decimalsOther);
    return kalmPrice;
}
```

## Recommendation
Revise current execution logic of _kalmPrice()/_getLpPrice() to defensively detect any manipulation attempts in the kalm Token/lp Token prices.
