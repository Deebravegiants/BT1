# [H] Velodrome LP Share calculation wont work for all velodrome pools

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-06-19
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/24
Type: hats-finding

## Details
**Github username:** @abhishekvispute
**Submission hash (on-chain):** 0x6c095881eb903abb853914dd88ca7962750a9620cae6633e1c70e0a869790d8b
**Severity:** high severity

**Description:**
## Description
VMEX intends to allow Velo LP tokens as an asset for their lending protocol.
The value of Velo LP token is derived inside `VelodromeOracle` library, and does take reserve's spot manipulation into consideration.
The formula used by VMEX team is following. 

![image](https://user-images.githubusercontent.com/46760063/246946370-ad809f8c-3e35-4789-ae9d-9cecefcfc352.png)

Source: https://blog.alphaventuredao.io/fair-lp-token-pricing/

As expected this derivation of LP share price sustains any spot reserve's manipulation since the product of `r0 * r1 (k)` remains the same.
However, there is a case where this formula doesn't work.

Velodrome supports two types of pools, stable pools, and variable pools.
Stable pools are designed for stable pairs like USDC- DAI, and variable pools are for more volatile assets.
Both pools operate from same pair contract and have almost all logic same (mint, burn).
However differ in calculation of K, and swapped amount.
https://github.com/velodrome-finance/contracts/blob/de6b2a19b5174013112ad41f07cf98352bfe1f24/contracts/Pair.sol#L437
Variable pools, follow uniswap's `xy = k` curve, and stable pools follow solidly's curve `x^3 * y + y^3 * x = k`.
This difference is not ignorable like VMEX incorrectly assumes [here](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/oracles/VelodromeOracle.sol#L8) 
```
//some minor differences to univ2 pairs, but mostly the same
```
It's not "mostly same", please check following to see how the above formula fails for the stable pools. 

Consider following as the initial stage of the Pool 
```
Reserve 0	1000000
Reserve 1	1000000
Price 0	  1
Price 1	  1
Total Supply	1000
Calculated Price Of LP Share	2000
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/24_
