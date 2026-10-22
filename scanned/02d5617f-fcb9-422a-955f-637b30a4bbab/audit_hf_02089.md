# [H] Incorrect Value Calculation in VelodromPoolAdapter_qStablePair

## Summary
Severity: High
Contest weight: 0.8139
Dataset id: 11792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Cadabra protocol provides a specific adapter to interact with the Velodrome pools. In the process of analyzing the logic to calculate the managed assets value, we notice the current approach to calculate the asset value should be revisited. In the following, we show the implementation of the related _values() routine. This routine is designed to measure the pool value under investment. The measurement relies on the use of _convertibleToken. For simplicity, we illustrate with one execution path, i.e., IS_TOKEN1_QUOTE_IN_BASE_POOL and IS_TOKEN1_QUOTE_IN_QUOTE_POOL are both true. With that, while the first step (line 79) is properly executed to calculate the initial price0, the next step examines the QUOTE_POOL to compute the final price0 = VelodromeUtils.amount1(price0, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE)* QUOTE_PRICE_FACTOR, instead of current price0 = VelodromeUtils.amount1(price0, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE)* QUOTE_PRICE_FACTOR (line 82). The reason is the common _convertibleToken in QUOTE_POOL becomes token0, hence using BASE1 as base0 and QUOTE_BASE as base1. The same issue also affects other execution paths.
```solidity
function _values(uint256 _amount0, uint256 _amount1) internal view override returns (uint256 _value0, uint256 _value1) {
    (uint r0, uint r1) = VelodromeUtils.reserves(address(POOL));
    (uint qr0, uint qr1) = VelodromeUtils.reserves(address(QUOTE_POOL));
    uint price0;
    uint price1;
    if (IS_TOKEN1_QUOTE_IN_BASE_POOL) {
        // TOKEN0(POOL) -> TOKEN1(POOL)
        price0 = VelodromeUtils.amount1(BASE0, BASE0, BASE1, r0, r1, IS_BASE_POOL_STABLE);
        if (IS_TOKEN1_QUOTE_IN_QUOTE_POOL) {
            // TOKEN1(POOL) -> TOKEN1(QUOTE_POOL)
            price0 = VelodromeUtils.amount1(price0, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount1(BASE1, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        } else {
            // TOKEN1(POOL) -> TOKEN0(QUOTE_POOL)
            price0 = VelodromeUtils.amount0(price0, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount0(BASE1, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        }
    } else {
        // TOKEN1(POOL) -> TOKEN0(POOL)
        price1 = VelodromeUtils.amount0(BASE1, BASE0, BASE1, r0, r1, IS_BASE_POOL_STABLE);
        if (IS_TOKEN1_QUOTE_IN_QUOTE_POOL) {
            // TOKEN0(POOL) -> TOKEN1(QUOTE_POOL)
            price0 = VelodromeUtils.amount1(BASE0, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount1(price1, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        } else {
            // TOKEN0(POOL) -> TOKEN0(QUOTE_POOL)
            price0 = VelodromeUtils.amount0(BASE1, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount0(price1, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        }
    }
    _value0 = _amount0 * price0 / BASE0;
    _value1 = _amount1 * price1 / BASE1;
}
```

## Recommendation
Revise the above routine as follows.
```solidity
function _values(uint256 _amount0, uint256 _amount1) internal view override returns (uint256 _value0, uint256 _value1) {
    (uint r0, uint r1) = VelodromeUtils.reserves(address(POOL));
    (uint qr0, uint qr1) = VelodromeUtils.reserves(address(QUOTE_POOL));
    uint price0;
    uint price1;
    if (IS_TOKEN1_QUOTE_IN_BASE_POOL) {
        // TOKEN0(POOL) -> TOKEN1(POOL)
        price0 = VelodromeUtils.amount1(BASE0, BASE0, BASE1, r0, r1, IS_BASE_POOL_STABLE);
        if (IS_TOKEN1_QUOTE_IN_QUOTE_POOL) {
            // TOKEN1(POOL) -> TOKEN1(QUOTE_POOL)
            price0 = VelodromeUtils.amount1(price0, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount1(BASE1, BASE1, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        } else {
            // TOKEN1(POOL) -> TOKEN0(QUOTE_POOL)
            price0 = VelodromeUtils.amount0(price0, BASE1, QUOTE_BASE, qr1, qr0, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount0(BASE1, BASE1, QUOTE_BASE, qr1, qr0, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        }
    } else {
        // TOKEN1(POOL) -> TOKEN0(POOL)
        price1 = VelodromeUtils.amount0(BASE1, BASE0, BASE1, r0, r1, IS_BASE_POOL_STABLE);
        if (IS_TOKEN1_QUOTE_IN_QUOTE_POOL) {
            // TOKEN0(POOL) -> TOKEN1(QUOTE_POOL)
            price0 = VelodromeUtils.amount1(BASE0, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount1(price1, BASE0, QUOTE_BASE, qr0, qr1, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        } else {
            // TOKEN0(POOL) -> TOKEN0(QUOTE_POOL)
            price0 = VelodromeUtils.amount0(BASE1, BASE0, QUOTE_BASE, qr1, qr0, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
            price1 = VelodromeUtils.amount0(price1, BASE0, QUOTE_BASE, qr1, qr0, IS_QUOTE_POOL_STABLE) * QUOTE_PRICE_FACTOR;
        }
    }
    _value0 = _amount0 * price0 / BASE0;
    _value1 = _amount1 * price1 / BASE1;
}
```
