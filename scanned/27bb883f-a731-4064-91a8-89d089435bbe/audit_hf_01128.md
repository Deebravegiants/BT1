# [M] Hardcoded tickSpacing prevents users to create pools with desired values

## Summary
Severity: Medium
Reporter: zanderbyte
Contest weight: 0.8112
Dataset id: 4617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Airlock contract, which manages the setup and migration of Doppler protocol, users are expected to specify their desired parameters such as the number of tokens to sell, the numeraire token, starting tick, etc... The Doppler::beforeInitialize hook includes a check to enforce a MAXIMUM_TICK_SPACING value to ensure tick spacing remains within valid bounds:
```solidity
int24 constant MAX_TICK_SPACING = 30;

function beforeInitialize(
    address,
    PoolKey calldata key,
    uint160
) external override onlyPoolManager returns (bytes4) {
    // Enforce maximum tick spacing
    if (key.tickSpacing > MAX_TICK_SPACING) revert InvalidTickSpacing();
}
```
However, if we take a look in UniswapV4Initializer::initialize() function, we can see that the tickSpacing is hardcoded to 8:
```solidity
PoolKey memory poolKey = PoolKey({
    currency0: isToken0 ? Currency.wrap(asset) : Currency.wrap(numeraire),
    currency1: isToken0 ? Currency.wrap(numeraire) : Currency.wrap(asset),
    hooks: IHooks(doppler),
    fee: 3000,
    tickSpacing: 8 // <<<
});
```
As a result, users with specific requirements based on their strategy, cannot create a pool with a custom tickSpacing. In addition, the dev team confirms that by stating that they should allow for variable tickSpacing.

## Proof of Concept
We can use the already existing test in UniswapV4Initializer.t.sol. Changing the DEFAULT_TICK_SPACING value in the DopplerConfig struct will show us that this value is never used upon creation of a pool in UniswapV4Initializer.sol.
```solidity
function test_v4initialize_TickSpacing() public {
    DopplerConfig memory config = DopplerConfig({
        numTokensToSell: DEFAULT_NUM_TOKENS_TO_SELL,
        minimumProceeds: DEFAULT_MINIMUM_PROCEEDS,
        maximumProceeds: DEFAULT_MAXIMUM_PROCEEDS,
        startingTime: block.timestamp + DEFAULT_STARTING_TIME,
        endingTime: block.timestamp + DEFAULT_ENDING_TIME,
        gamma: DEFAULT_GAMMA,
        epochLength: DEFAULT_EPOCH_LENGTH,
        fee: DEFAULT_FEE,
        tickSpacing: 10, // <<<
        numPDSlugs: DEFAULT_NUM_PD_SLUGS
    });
    address numeraire = address(0);
    bytes memory tokenFactoryData =
        abi.encode("Best Token", "BEST", 1e18, 365 days, new address[](0), new uint256[](0));
    bytes memory governanceFactoryData = abi.encode("Best Token");
    uint160 sqrtPrice = TickMath.getSqrtPriceAtTick(DEFAULT_START_TICK);
    bytes memory poolInitializerData = abi.encode(
        sqrtPrice,
        config.minimumProceeds,
        config.maximumProceeds,
        config.startingTime,
        config.endingTime,
        DEFAULT_START_TICK,
        DEFAULT_END_TICK,
        config.epochLength,
        config.gamma,
        false, // isToken0 will always be false using native token
        config.numPDSlugs
    );
    (bytes32 salt, address hook, address token) = mineV4(
        MineV4Params(
            address(airlock),
            address(manager),
            config.numTokensToSell,
            config.numTokensToSell,
            numeraire,
            ITokenFactory(address(tokenFactory)),
            tokenFactoryData,
            initializer,
            poolInitializerData
        )
    );
    deal(address(this), 100_000_000 ether);
    (address asset, address pool,,,) = airlock.create(
        CreateParams(
            config.numTokensToSell,
            config.numTokensToSell,
            numeraire,
            tokenFactory,
            tokenFactoryData,
            governanceFactory,
            governanceFactoryData,
            initializer,
            poolInitializerData,
            migrator,
            "",
            address(this),
            salt
        )
    );
    assertEq(pool, hook, "Wrong pool");
    assertEq(asset, token, "Wrong asset");
}
```
By logging the tickSpacing in Doppler::beforeInitialize() function, we can see that this value is always 8:
```solidity
function beforeInitialize(
    address,
    PoolKey calldata key,
    uint160
) external override onlyPoolManager returns (bytes4) {
    if (isInitialized) revert AlreadyInitialized();
    isInitialized = true;
    poolKey = key;
    // Enforce maximum tick spacing
    if (key.tickSpacing > MAX_TICK_SPACING) revert InvalidTickSpacing();
    console.log("tickSpacing", uint256(int256(key.tickSpacing)));
    /* Gamma checks */
    // Enforce that the total tick delta is divisible by the total number of epochs
    // Enforce that gamma is divisible by tick spacing
    if (gamma % key.tickSpacing != 0) revert InvalidGamma();
    return BaseHook.beforeInitialize.selector;
}
```

## Recommendation
Refactor the UniswapV4Initializer.sol contract to allow users to specify their desired tickSpacing during pool creation.
