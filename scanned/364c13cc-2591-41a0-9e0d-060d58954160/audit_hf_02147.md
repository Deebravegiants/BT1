# [M] Proper Protocol Fee Calculation in DMMPool

## Summary
Severity: Medium
Contest weight: 0.6072
Dataset id: 12036
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier in Section 3.7, the Evrynet protocol has the built-in Dynamic Automated Market Making (DMM)-based DEX functionality. And the provided DEX is customized with a reconﬁgurable trade fee and protocol fee. While examining the protocol fee extraction, we notice the current implementation is inconsistent with the intended protocol fee percentage governmentFeeBps.

```solidity
/// @dev if fee is on, mint liquidity equivalent configured fee of the growth sqrt(k)
function _mintFee(bool isAmpPool, ReserveData memory data) internal returns (bool feeOn) {
    (address feeTo, uint16 governmentFeeBps,) = factory.getFeeConfiguration();
    feeOn = (feeTo != address(0) && governmentFeeBps != 0);
    uint256 _kLast = kLast; // gas savings
    if (feeOn) {
        if (_kLast != 0) {
            uint256 rootK = MathExt.sqrt(getK(isAmpPool, data));
            uint256 rootKLast = MathExt.sqrt(_kLast);
            if (rootK > rootKLast) {
                uint256 numerator = totalSupply().mul(rootK.sub(rootKLast)).mul(governmentFeeBps);
                uint256 denominator = rootK.add(rootKLast).mul(5000);
                uint256 liquidity = numerator / denominator;
                if (liquidity > 0) _mint(feeTo, liquidity);
            } else if (_kLast != 0) {
                kLast = 0;
            }
        }
    }
}
```

To elaborate, we show above the _mintFee() routine inside the the evry-finance-dmm-swap repos-itory. Note the trade fee collection at the time of the trade would impose an additional gas cost on every trade. To avoid this, accumulated fees are collected only when liquidity is deposited or withdrawn. The contract computes the accumulated fees, and mints new liquidity tokens to the fee beneﬁciary, immediately before any tokens are minted or burned (via the above _mintFee() routine). It comes to our attention the accumulated fees should be computed as k2 (1+fee1) k2+k1 totalSupply(), i.e., k2-k1) governmentFeeBps (BPS-govermentFeeBps) k2+k1 governmentFeeBps totalSupply().

## Recommendation
Revise the above _mintFee() function to properly collect the protocol fee. An example revision is shown as follows:

```solidity
/// @dev if fee is on, mint liquidity equivalent configured fee of the growth sqrt(k)
function _mintFee(bool isAmpPool, ReserveData memory data) internal returns (bool feeOn) {
    (address feeTo, uint16 governmentFeeBps,) = factory.getFeeConfiguration();
    feeOn = (feeTo != address(0) && governmentFeeBps != 0);
    uint256 _kLast = kLast; // gas savings
    if (feeOn) {
        if (_kLast != 0) {
            uint256 rootK = MathExt.sqrt(getK(isAmpPool, data));
            uint256 rootKLast = MathExt.sqrt(_kLast);
            if (rootK > rootKLast) {
                uint256 numerator = totalSupply().mul(rootK.sub(rootKLast)).mul(governmentFeeBps);
                uint256 denominator = rootK.mul(BPS.sub(governmentFeeBps)).add(rootKLast.mul(governmentFeeBps));
                uint256 liquidity = numerator / denominator;
                if (liquidity > 0) _mint(feeTo, liquidity);
            } else if (_kLast != 0) {
                kLast = 0;
            }
        }
    }
}
```
