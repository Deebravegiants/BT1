# [H] addLiquidity(...) can be griefed

## Summary
Severity: High
Contest weight: 0.3289
Dataset id: 7218
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can DoS/block another use to provide liquidity to the Hyperdrive. The attack works as follows:
1. The attacker frontruns a transaction that would call addLiquidity(...) by opening the maximum possible short. In case of no or small outstanding longs ( L0_c ≈ 0 ), the attacker can reduce the z to a number close to 0 such that:
APR = (1 - z/y)^(ts/tnorm_pos) / (z/y)^ts
blows up to a really big number since the denominator or z/y^ts would be a really small number such the apr = HyperdriveMath.calculateAPRFromReserves(...) would not be less than or equal to _maxApr provided by the user in the next transaction. The attacker might also be able to trigger division by z/y = 0 revert.
2. The user's transaction of calling addLiquidity(...) would be processed and reverted due to above. Even if the user sets _maxApr = type(uint256).max, the attacker can take advantage of the division by 0 case or if that is not possible the following calculation of lpShares would underflow and revert due to the fact that endingPresentValue < startingPresentValue:
lpShares = (endingPresentValue - startingPresentValue).mulDivDown(
    lpTotalSupply,
    startingPresentValue
);
This line of attack is similar to the ones used in the below issues where the attacker tries to open a short with the maximum possible amount:
• Sandwich a call to addLiquidity(...) for profit
• Drain pool by sandwiching matured shorts

## Recommendation
More analysis needs to be performed to avoid issues like above, as having z really small is not desirable in many cases.
A few things can be added to prevent the division by 0 attack. If the liquidity provider sets _minApr = 0 and _maxApr = type(uint256).max, the calculation of apr and the bound checks below can be avoided.
uint256 apr = HyperdriveMath.calculateAPRFromReserves(
    _marketState.shareReserves,
    _marketState.bondReserves,
    _initialSharePrice,
    _positionDuration,
    _timeStretch
);
if (apr < _minApr || apr > _maxApr) revert Errors.InvalidApr();
