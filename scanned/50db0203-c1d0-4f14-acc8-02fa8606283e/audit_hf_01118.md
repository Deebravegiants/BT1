# [H] Airlock.migrate attempts to transfer native ETH on safeTransfer calls

## Summary
Severity: High
Reporter: jovi.eth, also found by AngryMustacheMan, rokinot, zanderbyte, trachev, etherhood, valkvalue, Aamirusmani1552, saucier a
Contest weight: 1.0000
Dataset id: 4589
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The migrate function at the Airlock contract executes two transfers to the liquidity migrator, one of token0 and a second one of token1:
```solidity
function migrate(
    address asset
) external {
    // ...
    ERC20(token0).safeTransfer(address(assetData.liquidityMigrator), total0);
    ERC20(token1).safeTransfer(address(assetData.liquidityMigrator), total1);
    // ...
}
```
The utilized safeTransfer library is Solady's. According to its implementation, it will attempt to execute an ERC20 contract call to the destination, but message value will be zero:
```solidity
let success := call(gas(), token, 0, 0x10, 0x44, 0x00, 0x20)
```
at solady/src/utils/ext/zksync/SafeTransferLib.sol at d355d147f150844ddf55ffbb63fcd0130ac73fb4 · Vectorized/solady.
This means the current implementation is not able to transfer native tokens.

## Proof of Concept
Make sure to import console.sol at the Airlock contract:
```solidity
import "forge-std/console.sol";
```
Then add the logs at the following lines of code of the migrate function:
```solidity
console.log("Balance logs:");
console.log(total0);
ERC20(token0).safeTransfer(address(assetData.liquidityMigrator), total0);
console.log(address(this).balance);
console.log(address(assetData.liquidityMigrator).balance);
ERC20(token1).safeTransfer(address(assetData.liquidityMigrator), total1);
```
Paste the test at Airlock.t.sol:
```solidity
function test_migrate_poc() public {
    (address hook, address asset) = test_create_DeploysV4();
    PoolKey memory poolKey = PoolKey({
        currency0: Currency.wrap(address(0)),
        currency1: Currency.wrap(asset),
        fee: 3000,
        tickSpacing: DEFAULT_TICK_SPACING,
        hooks: IHooks(hook)
    });
    // Deploy swapRouter
    swapRouter = new PoolSwapTest(manager);
    V4Quoter quoter = new V4Quoter(manager);
    CustomRouter router = new CustomRouter(swapRouter, quoter, poolKey, false, true);
    uint256 amountIn = router.computeBuyExactOut(DEFAULT_MIN_PROCEEDS);
    deal(address(this), amountIn);
    router.buyExactOut{ value: amountIn }(DEFAULT_MIN_PROCEEDS);
    vm.warp(block.timestamp + DEFAULT_EPOCH_LENGTH);
    amountIn = router.computeBuyExactOut(DEFAULT_MIN_PROCEEDS);
    deal(address(this), amountIn);
    router.buyExactOut{ value: amountIn }(DEFAULT_MIN_PROCEEDS);
    vm.warp(DEFAULT_ENDING_TIME);
    airlock.migrate(asset);
}
```
Run it with the following command:
forge test --match-test test_migrate_poc -vv.
Notice the high-level logs, it displays the native currency won't be transferred at the safeTransfer call leading to a safe transfer fail. Relevant output:
Balance logs:
1083479745851064649
1093958189761634497
address weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
token0 = token0 == address(0) ? address(weth) : token0;
token0.call{ value: address(this).balance }(""); // could be msg.value
ERC20(token0).safeTransfer(address(assetData.liquidityMigrator), ERC20(token0).balanceOf(address(this)));
ERC20(token1).safeTransfer(address(assetData.liquidityMigrator), total1);

## Recommendation
No data
