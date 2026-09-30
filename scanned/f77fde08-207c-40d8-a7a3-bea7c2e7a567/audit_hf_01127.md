# [M] If there hasn't been an update for more than an epoch prior to migration, migration will happen at wrong price

## Summary
Severity: Medium
Reporter: deadrosesxyz
Contest weight: 0.6625
Dataset id: 4616
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
if (isMigration) {
    BalanceDelta totalCallerDelta;
    BalanceDelta totalFeesAccrued;
    for (uint256 i = 1; i < NUM_DEFAULT_SLUGS + numPDSlugs; ++i) {
        Position memory position = positions[bytes32(i)];
        if (position.liquidity != 0) {
            (BalanceDelta callerDelta, BalanceDelta feesAccrued) = poolManager.modifyLiquidity(
                key,
                IPoolManager.ModifyLiquidityParams({
                    tickLower: isToken0 ? position.tickLower : position.tickUpper,
                    tickUpper: isToken0 ? position.tickUpper : position.tickLower,
                    liquidityDelta: -int128(position.liquidity),
                    salt: bytes32(uint256(position.salt))
                }),
                ""
            );
            totalCallerDelta = add(totalCallerDelta, callerDelta);
            totalFeesAccrued = add(totalFeesAccrued, feesAccrued);
        }
    }
}
```
The problem is that if when ending timestamp is crossed, there hasn't been rebalancing for more than an epoch, the price wouldn't be lowered for the inactivity in these last few epochs (although it should be). This would result in migration happening at higher price than expected and ultimately not following the intended functionality.

Impact Explanation:
Pool will migrate at wrong price.

## Proof of Concept
Add the following PoCs to Airlock.t.sol. In the first one there isn't an update throughout the last epoch and as a result it migrates at ~2% higher price. Although it actually has even less buy activity than in the second test:
```solidity
function test_migratesAtWrongPrice1() public {
    // vm.skip(true);
    (address hook, address asset) = test_create_DeploysV4();
    PoolKey memory poolKey = PoolKey({
        currency0: Currency.wrap(address(numeraire)),
        currency1: Currency.wrap(asset),
        fee: 3000,
        tickSpacing: DEFAULT_TICK_SPACING,
        hooks: IHooks(hook)
    });
    // Deploy swapRouter
    swapRouter = new PoolSwapTest(manager);
    V4Quoter quoter = new V4Quoter(manager);
    bool isToken0 = asset < address(numeraire) ? true : false;
    CustomRouter router = new CustomRouter(swapRouter, quoter, poolKey, isToken0, false);
    // changed isUsingEth to no
    vm.warp(DEFAULT_ENDING_TIME - 2* DEFAULT_EPOCH_LENGTH);
    uint256 amountIn = router.computeBuyExactOut(1e18);
    numeraire.mint(address(this), amountIn);
    numeraire.approve(address(router), amountIn);
    router.buyExactOut(1e18);
    vm.warp(DEFAULT_ENDING_TIME);
    airlock.migrate(asset);
    address pool = IUniswapV2Factory(UNISWAP_V2_FACTORY_MAINNET).getPair(address(numeraire), asset);
    (uint256 reserve0, uint256 reserve1,) = IUniswapV2Pair(pool).getReserves();
    uint256 reserveRatio = reserve0 * 1e18 / reserve1;
    console.log("reserve ratio %e", reserveRatio);
}

function test_migratesAtWrongPrice2() public {
    // vm.skip(true);
    (address hook, address asset) = test_create_DeploysV4();
    PoolKey memory poolKey = PoolKey({
        currency0: Currency.wrap(address(numeraire)),
        currency1: Currency.wrap(asset),
        fee: 3000,
        tickSpacing: DEFAULT_TICK_SPACING,
        hooks: IHooks(hook)
    });
    // Deploy swapRouter
    swapRouter = new PoolSwapTest(manager);
    V4Quoter quoter = new V4Quoter(manager);
    bool isToken0 = asset < address(numeraire) ? true : false;
    CustomRouter router = new CustomRouter(swapRouter, quoter, poolKey, isToken0, false);
    // changed isUsingEth to no
    vm.warp(DEFAULT_ENDING_TIME - 2* DEFAULT_EPOCH_LENGTH);
    uint256 amountIn = router.computeBuyExactOut(1e18);
    numeraire.mint(address(this), amountIn);
    numeraire.approve(address(router), amountIn);
    router.buyExactOut(1e18);
    vm.warp(DEFAULT_ENDING_TIME - 1);
    amountIn = router.computeBuyExactOut(100);
    numeraire.mint(address(this), amountIn);
    numeraire.approve(address(router), amountIn);
    router.buyExactOut(100);
    vm.warp(DEFAULT_ENDING_TIME);
    airlock.migrate(asset);
    address pool = IUniswapV2Factory(UNISWAP_V2_FACTORY_MAINNET).getPair(address(numeraire), asset);
    (uint256 reserve0, uint256 reserve1,) = IUniswapV2Pair(pool).getReserves();
    uint256 reserveRatio = reserve0 * 1e18 / reserve1;
    console.log("reserve ratio %e", reserveRatio);
}
```
The logs:
[PASS] test_migratesAtWrongPrice1() (gas: 22099531)
Logs:
reserve ratio 2.541753047290564e15
[PASS] test_migratesAtWrongPrice2() (gas: 23328216)
Logs:
reserve ratio 2.509427549047483e15

## Recommendation
Before migrating, run a rebalance.
