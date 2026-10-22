# [H] IndexPool’s `INIT_POOL_SUPPLY` is not fair.

## Summary
Severity: High
Contest weight: 0.1988
Dataset id: 933
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `indexPool` mint `INIT_POOL_SUPPLY` to address 0 in the constructor. However, the value of the burned lp is decided by the first lp provider. According to the formula in [`IndexPool.sol` L106](https://github.com/sushiswap/trident/blob/9130b10efaf9c653d74dc7a65bde788ec4b354b5/contracts/pool/IndexPool.sol#L106).

`AmountIn = first_lp_amount / INIT_POOL_SUPPLY` and the burned lp worth = `AmountIn * (INIT_POOL_SUPPLY) / (first_lp_amount + INIT_POOL_SUPPLY)`. If a pool is not initialized with optimal parameters, it would be a great number of tokens been burn. All lp providers in the pool would receive less profit.

The optimal parameter is `10**8`. It’s likely no one would initialize with `10**8` wei in most pools. I consider this is a high-risk issue.

## Recommendation
Recommend to handle `INIT_POOL_SUPPLY` in uniswap-v2’s way. Determine an optimized parameter for the user would be a better UX design.
