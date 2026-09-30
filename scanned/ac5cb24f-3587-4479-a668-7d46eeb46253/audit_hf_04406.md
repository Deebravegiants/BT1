# [M] `Stable2::calcLpTokenSupply`

## Summary
Severity: Medium
Contest weight: 0.7617
Dataset id: 21822
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`calcLpTokenSupply` is used in both `calcReserveAtRatioLiquidity` and `calcReserveAtRatioSwap`, we’ll focus on `calcReserveAtRatioLiquidity`.

`calcLpTokenSupply` is called inside `calcRate` here:
```solidity
    function calcReserveAtRatioLiquidity(
            uint256[] calldata reserves,
            uint256 j,
            uint256[] calldata ratios,
            bytes calldata data
        ) external view returns (uint256 reserve) {
    ...
    for (uint256 k; k < 255; k++) {
                scaledReserves[j] = updateReserve(pd, scaledReserves[j]);
                // calculate new price from reserves:
                pd.newPrice = calcRate(scaledReserves, i, j, abi.encode(18, 18));
    ...
```

Inside we call the function:
```solidity
    function calcRate(
            uint256[] memory reserves,
            uint256 i,
            uint256 j,
            bytes memory data
        ) public view returns (uint256 rate) {
            uint256[] memory decimals = decodeWellData(data);
            uint256[] memory scaledReserves = getScaledReserves(reserves, decimals);

            // calc lp token supply (note: `scaledReserves` is scaled up, and does not require bytes).
            uint256 lpTokenSupply = calcLpTokenSupply(scaledReserves, abi.encode(18, 18));
            rate = _calcRate(scaledReserves, i, j, lpTokenSupply);
        }
```

Note that the only change to `calcLpTokenSupply` is the added revert on the last line of the function.
```solidity
    function calcLpTokenSupply(
            uint256[] memory reserves,
            bytes memory data
        ) public view returns (uint256 lpTokenSupply) {
            if (reserves[0] == 0 && reserves[1] == 0) return 0;
            uint256[] memory decimals = decodeWellData(data);
            // scale reserves to 18 decimals.
            uint256[] memory scaledReserves = getScaledReserves(reserves, decimals);

            uint256 Ann = a * N * N;
            
            uint256 sumReserves = scaledReserves[0] + scaledReserves[1];
            lpTokenSupply = sumReserves;
            for (uint256 i = 0; i < 255; i++) {
                uint256 dP = lpTokenSupply;
                // If division by 0, this will be borked: only withdrawal will work. And that is good
                dP = dP * lpTokenSupply / (scaledReserves[0] * N);
                dP = dP * lpTokenSupply / (scaledReserves[1] * N);
                uint256 prevReserves = lpTokenSupply;
                lpTokenSupply = (Ann * sumReserves / A_PRECISION + (dP * N)) * lpTokenSupply
                    / (((Ann - A_PRECISION) * lpTokenSupply / A_PRECISION) + ((N + 1) * dP));
                // Equality with the precision of 1
                if (lpTokenSupply > prevReserves) {
                    if (lpTokenSupply - prevReserves <= 1) return lpTokenSupply;
                } else {
                    if (prevReserves - lpTokenSupply <= 1) return lpTokenSupply;
                }
            }
            revert("Non convergence: calcLpTokenSupply");
        }
```

The issue here lies that `calcLpTokenSupply` reverts under certain circumstances since it cannot converge, which makes the whole call to `calcReserveAtRatioLiquidity` revert. We’ll investigate this further inside the PoC section.

## Proof of Concept
Paste the following inside `BeanstalkStable2LiquidityTest` and run `forge test --mt test_calcReserveAtRatioLiquidity_equal_equalPositive -vv`. This is a rough test to loop through some of the cases in `Stable2LUT1`.
```solidity
    function test_calcReserveAtRatioLiquidity_equal_equalPositive() public view {
            uint256[] memory reserves = new uint256[](2);
            reserves[0] = 1987e18;
            reserves[1] = 12345e8;
            uint256[] memory ratios = new uint256[](2);
            ratios[0] = 1e18;
            ratios[1] = 1e18;

            for(uint i; i < 10000; i++) {
                _f.calcReserveAtRatioLiquidity(reserves, 0, ratios, data);
                ratios[0] += 0.003e18;
            }
        }
```

You’ll notice that the test reverts with `[FAIL. Reason: revert: Non convergence: calcLpTokenSupply]`.

The values that it reverts with are:
```
      Ratios[0]:      7195000000000000000 
      Ratios[1]:      1000000000000000000
      Target price:   138927
      High Price:     277020
      Low Price:      1083
      Current price:  1083 (price is closer to lowPrice)
```

This is when we hit this case in `Stable2LUT1`:
```
     if (price < 0.001083e6) {
                                        revert("LUT: Invalid price");
                                    } else {
                                        return
                 ->                         PriceData(0.27702e6, 0, 9.646293093274934449e18, 0.001083e6, 0, 2000e18, 1e18);
                                    }
```

Here are the last few iterations of `calcLpTokenSupply`:
```
     Current Lp token supply:  237151473819804594336
      Prev Lp token supply:     237151473819804594338
      -------------------------------------------
      Current Lp token supply:  237151473819804594338
      Prev Lp token supply:     237151473819804594336
      -------------------------------------------
      Current Lp token supply:  237151473819804594336
      Prev Lp token supply:     237151473819804594338
      -------------------------------------------
      Current Lp token supply:  237151473819804594338
      Prev Lp token supply:     237151473819804594336
      -------------------------------------------
      Current Lp token supply:  237151473819804594336
      Prev Lp token supply:     237151473819804594338
      -------------------------------------------
      Current Lp token supply:  237151473819804594338
      Prev Lp token supply:     237151473819804594336
      -------------------------------------------
```

As you can see, the values "loop" `+-2`; which makes it impossible to converge since the difference has to be `<= 1` so it converges.

Something to note is that even if we change the `reserves` in the test, the test continues failing with the same error, but every test fails when we hit this specific case in the lookup table and the price is closer to the `lowPrice`.

`PriceData(0.27702e6, 0, 9.646293093274934449e18, 0.001083e6, 0, 2000e18, 1e18);`

It’s unclear what causes this "looping" to occur, so it’s hard to say what the root cause is.

Something interesting is that this started happening once the revert was introduced, the last audit didn’t have it, but the code still worked. Then it didn’t revert it just returned the last `lpTokenSupply`.

Also note that the underlying issue is in `calcLpTokenSupply`, so if the function is used on its own it can still revert, but it happens much more often when `calcReserveAtRatioLiquidity` is used.

## Recommendation
It’s very hard to recommend a fix here, as many tweaks can fix the issue. We recommend:

  1. Passing a flag to `calcLpTokenSupply`, if true then if the function doesn't converge it won’t revert.
  2. Tweaking the `PriceData` values for the specific case in the lookup table, narrowing down the range seems to fix the issue.
