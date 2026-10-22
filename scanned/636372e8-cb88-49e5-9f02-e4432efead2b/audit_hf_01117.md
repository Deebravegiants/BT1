# [H] Migration will be impossible in case token has vesting recipients

## Summary
Severity: High
Reporter: deadrosesxyz, also found by Aamirusmani1552, trachev and KupiaSec
Contest weight: 1.0000
Dataset id: 4588
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating a token, user can specify vesting recipients. In this case, the tokens are minted to the token contract itself, and recipients have to claim them directly. Then, only the remaining of the initial supply is minted to the Airlock:
```solidity
for (uint256 i; i < length; ++i) {
    uint256 amount = amounts_[i];
    getVestingDataOf[recipients_[i]].totalAmount += amount;
    require(
        getVestingDataOf[recipients_[i]].totalAmount <= maxPreMintPerAddress,
        MaxPreMintPerAddressExceeded(getVestingDataOf[recipients_[i]].totalAmount, maxPreMintPerAddress)
    );
    vestedTokens += amount;
}
uint256 maxTotalPreMint = initialSupply * MAX_TOTAL_PRE_MINT_WAD / 1 ether;
require(vestedTokens <= maxTotalPreMint, MaxTotalPreMintExceeded(vestedTokens, maxTotalPreMint));
if (vestedTokens > 0) {
    _mint(address(this), vestedTokens);
}
_mint(recipient, initialSupply - vestedTokens);
```
However, when migrating, the Airlock contract assumes it holds all asset tokens which are not sent initially to be sold on univ3/v4. And it attempts to send these tokens to the migrator.
```solidity
if (token0 == asset) {
    total0 += assetData.totalSupply - assetData.numTokensToSell;
    // assumes it holds all of the non-sold tokens
} else {
    total1 += assetData.totalSupply - assetData.numTokensToSell;
}
ERC20(token0).safeTransfer(address(assetData.liquidityMigrator), total0);
ERC20(token1).safeTransfer(address(assetData.liquidityMigrator), total1);
```
For this reason, if there are any vesting recipients, the following transfer would fail, due to insufficient funds. As this would brick migration, it would make the asset tokens worthless and all of the numeraire collected will be stuck.

Impact Explanation:
As migration would be stuck and all funds would be lost, High is appropriate.

## Proof of Concept
Add the following test to Airlock.t.sol:
```solidity
function test_migrateAirlock() public {
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
    vm.warp(DEFAULT_ENDING_TIME - 1);
    uint256 amountIn = router.computeBuyExactOut(0.5e27);
    numeraire.mint(address(this), amountIn);
    numeraire.approve(address(router), amountIn);
    router.buyExactOut(0.5e27);
    vm.warp(DEFAULT_ENDING_TIME);
    vm.expectRevert("TRANSFER_FAILED");
    airlock.migrate(asset);
}
```
You'd also have to set up the test suite to provide vested tokens as follows:
```solidity
function test_create_DeploysV4() public returns (address, address) {
    address[] memory users = new address[](2);
    // @audit - comment out if airdrop is not present.
    users[0] = address(1337);
    users[1] = address(1338);
    uint256[] memory amounts = new uint256[](2);
    amounts[0] = 1e25;
    amounts[1] = 1e25;
    bytes memory tokenFactoryData =
        abi.encode(DEFAULT_TOKEN_NAME, DEFAULT_TOKEN_SYMBOL, 0, 0, users, amounts);
    // changed here to include airdrop users
    uint160 sqrtPrice = TickMath.getSqrtPriceAtTick(DEFAULT_START_TICK);
    bytes memory poolInitializerData = abi.encode(
        sqrtPrice,
        0,
        // @audit, changed from DEFAULT_MIN_PROCEEDS
        DEFAULT_MAX_PROCEEDS,
        DEFAULT_STARTING_TIME,
        DEFAULT_ENDING_TIME,
        DEFAULT_START_TICK,
        DEFAULT_END_TICK,
        DEFAULT_EPOCH_LENGTH,
        DEFAULT_GAMMA,
        false,
        DEFAULT_PD_SLUGS
    );
    (bytes32 salt, address hook, address asset) = mineV4(
        MineV4Params(
            address(airlock),
            address(manager),
            DEFAULT_INITIAL_SUPPLY,
            DEFAULT_INITIAL_SUPPLY - 2e25,
            address(numeraire), // changed from address(0)
            tokenFactory,
            tokenFactoryData,
            uniswapV4Initializer,
            poolInitializerData
        )
    );
    airlock.create(
        CreateParams(
            DEFAULT_INITIAL_SUPPLY,
            DEFAULT_INITIAL_SUPPLY - 2e25,
            // setting numTokensToSell
            address(numeraire), // changed from address(0)
            tokenFactory,
            tokenFactoryData,
            governanceFactory,
            abi.encode(DEFAULT_TOKEN_NAME),
            uniswapV4Initializer,
            poolInitializerData,
            uniswapV2LiquidityMigrator,
            new bytes(0),
            address(0xb0b),
            salt
        )
    );
    return (hook, asset);
}
```
Also, set up a numeraire asset within the test contract.
```solidity
TestERC20 numeraire;

function setUp() public {
    vm.createSelectFork(vm.envString("MAINNET_RPC_URL"), 21_093_509);
    vm.warp(DEFAULT_STARTING_TIME);
    numeraire = new TestERC20(1e18);
```

## Recommendation
Account for the vested tokens.
