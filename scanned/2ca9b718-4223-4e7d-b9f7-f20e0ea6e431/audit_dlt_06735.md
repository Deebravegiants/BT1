# [M] `PendlePowerManager` is incompatible with `PendleRouterV3`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-wise-lending
Published: 2024-03-10
Source: https://github.com/code-423n4/2024-02-wise-lending-findings/issues/133
Type: code-finding

## Details
# Lines of code

https://github.com/pendle-finance/pendle-core-v2-public/blob/main/contracts/router/ActionAddRemoveLiqV3.sol#L166-L172
https://github.com/pendle-finance/pendle-core-v2-public/blob/main/contracts/router/ActionAddRemoveLiqV3.sol#L444-L449
https://github.com/code-423n4/2024-02-wise-lending/blob/main/contracts/PowerFarms/PendlePowerFarm/PendlePowerFarmLeverageLogic.sol#L467-L482
https://github.com/code-423n4/2024-02-wise-lending/blob/main/contracts/PowerFarms/PendlePowerFarm/PendlePowerFarmLeverageLogic.sol#L165-L171


# Vulnerability details

## Impact

`PendlePowerManager` is incompatible with the latest deployment of `PendleRouter` and will cause reverts when attempting to open a farm position.

## Proof of Concept

The latest deployment of the Pendle router, `PendleRouterV3`, is incompatible with the `PendlePowerManager` contract. The sponsor is expecting full compatibility with both but this is not the case here. The problem stems from the calls made to `PENDLE_ROUTER.removeLiquiditySingleSy()` and `PENDLE_ROUTER.addLiquiditySingleSy()`:

```solidity
function _logicOpenPosition(
    bool _isAave,
    uint256 _nftId,
    uint256 _depositAmount,
    uint256 _totalDebtBalancer,
    uint256 _allowedSpread
)
    internal
{
    // ...
    (
        uint256 netLpOut
        ,
    ) = PENDLE_ROUTER.addLiquiditySingleSy(
        {
            _receiver: address(this),
            _market: address(PENDLE_MARKET),
            _netSyIn: syReceived,
            _minLpOut: 0,
            _guessPtReceivedFromSy: ApproxParams(
                {
                    guessMin: netPtFromSwap - 100,
                    guessMax: netPtFromSwap + 100,
                    guessOffchain: 0,
                    maxIteration: 50,
                    eps: 1e15
                }
            )
        }
    );
  // ...
}

function _logicClosePosition(
    uint256 _nftId,
    uint256 _borrowShares,
    uint256 _lendingShares,
    uint256 _totalDebtBalancer,
    uint256 _allowedSpread,
    address _caller,
    bool _ethBack,
    bool _isAave
)
    private
{
    // ...
    (
        uint256 netSyOut
        ,
    ) = PENDLE_ROUTER.removeLiquiditySingleSy(
        {
            _receiver: address(this),
            _market: address(PENDLE_MARKET),
            _netLpToRemove: withdrawnLpsAmount,
            _minSyOut: 0
        }
    );
  // ...
}
```

The issue is that the signatures of those have changed in V3:

```solidity
function addLiquiditySingleSy(
    address receiver,
    address market,
    uint256 netSyIn,
    uint256 minLpOut,
    ApproxParams calldata guessPtReceivedFromSy,
    LimitOrderData calldata limit
) external returns (uint256 netLpOut, uint256 netSyFee);

function removeLiquiditySingleSy(
    address receiver,
    address market,
    uint256 netLpToRemove,
    uint256 minSyOut,
    LimitOrderData calldata limit
) external returns (uint256 netSyOut, uint256 netSyFee);
```

There's a new parameter called `limit` that's not accounted for in the calls in the `PendlePowerFarmLeverageLogic` helper contract. This will lead to calls always reverting with `RouterInvalidAction` due to Pendle's proxy not being able to locate the selector used.

Coded POC (`PendlePowerFarmControllerBase.t.sol`):

```solidity
function _setUpCustom(address _pendleRouter) private {
    _setProperties();

    pendleLockInstance = IPendleLock(AddressesMap[chainId].pendleLock);

    wethInstance = IWETH(AddressesMap[chainId].weth);

    wiseOracleHubInstance = WiseOracleHub(AddressesMap[chainId].oracleHub);

    aaveHubInstance = IAaveHub(AddressesMap[chainId].aaveHub);

    vm.startPrank(wiseLendingInstance.master());

    controllerTester = new PendleControllerTester(
        AddressesMap[chainId].vePendle,
        AddressesMap[chainId].pendleTokenAddress,
        AddressesMap[chainId].voterContract,
        AddressesMap[chainId].voterRewardsClaimer,
        AddressesMap[chainId].oracleHub
    );

    pendlePowerFarmTokenFactory = controllerTester.PENDLE_POWER_FARM_TOKEN_FACTORY();

    PoolManager.CreatePool memory params = PoolManager.CreatePool({
        allowBorrow: true,
        poolToken: AddressesMap[chainId].aweth,
        poolMulFactor: 17500000000000000,
        poolCollFactor: 805000000000000000,
        maxDepositAmount: 1800000000000000000000000
    });

    wiseLendingInstance.createPool(params);

    IAaveHub(AddressesMap[chainId].aaveHub).setAaveTokenAddress(
        AddressesMap[chainId].weth, AddressesMap[chainId].aweth
    );

    if (block.chainid == ETH_CHAIN_ID) {
        wiseOracleHubInstance.addOracle(
            AddressesMap[chainId].aweth,
            wiseOracleHubInstance.priceFeed(AddressesMap[chainId].weth),
            new address[](0)
        );

        wiseOracleHubInstance.recalibrate(AddressesMap[chainId].aweth);
    }

    _addPendleTokenOracle();

    _addPendleMarketOracle(
        AddressesMap[chainId].PendleMarketStEth,
        address(wiseOracleHubInstance.priceFeed(AddressesMap[chainId].weth)),
        AddressesMap[chainId].weth,
        2 ether,
        3 ether
    );

    IPendlePowerFarmToken derivativeToken =
        _addPendleMarket(AddressesMap[chainId].PendleMarketStEth, "name", "symbol", MAX_CARDINALITY);

    pendleChildLpOracleInstance = new PendleChildLpOracle(address(pendleLpOracleInstance), address(derivativeToken));

    address[] memory underlyingTokens = new address[](1);
    underlyingTokens[0] = AddressesMap[chainId].weth;

    wiseOracleHubInstance.addOracle(
        address(derivativeToken), IPriceFeed(address(pendleChildLpOracleInstance)), underlyingTokens
    );

    address[] memory underlyingTokensCurrent = new address[](0);

    wiseOracleHubInstance.addOracle(CRV_TOKEN_ADDRESS, IPriceFeed(CRV_ETH_FEED), underlyingTokensCurrent);

    wiseOracleHubInstance.recalibrate(CRV_TOKEN_ADDRESS);

    curveUsdEthOracleInstance = new CurveUsdEthOracle(IPriceFeed(ETH_USD_FEED), IPriceFeed(CRVUSD_USD_FEED));

    wiseOracleHubInstance.addOracle(
        CRVUSD_TOKEN_ADDRESS, IPriceFeed(address(curveUsdEthOracleInstance)), new address[](0)
    );

    wiseOracleHubInstance.recalibrate(CRVUSD_TOKEN_ADDRESS);

    wiseOracleHubInstance.addTwapOracle(
        CRV_TOKEN_ADDRESS,
        CRV_UNI_POOL_ADDRESS,
        CRV_UNI_POOL_TOKEN0_ADDRESS,
        CRV_UNI_POOL_TOKEN1_ADDRESS,
        UNI_V3_FEE_CRV_UNI_POOL
    );

    wiseOracleHubInstance.addTwapOracleDerivative(
        CRVUSD_TOKEN_ADDRESS,
        CRVUSD_UNI_POOL_TOKEN0_ADDRESS,
        [ETH_USDC_UNI_POOL_ADDRESS, CRVUSD_UNI_POOL_ADDRESS],
        [ETH_USDC_UNI_POOL_TOKEN0_ADDRESS, CRVUSD_UNI_POOL_TOKEN0_ADDRESS],
        [ETH_USDC_UNI_POOL_TOKEN1_ADDRESS, CRVUSD_UNI_POOL_TOKEN1_ADDRESS],
        [UNI_V3_FEE_ETH_USDC_UNI_POOL, UNI_V3_FEE_CRVUSD_UNI_POOL]
    );

    address underlyingFeed = CRVUSD_TOKEN_ADDRESS;

    _addPendleMarketOracle(
        CRVUSD_PENDLE_28MAR_2024, address(curveUsdEthOracleInstance), underlyingFeed, 0.0008 ether, 0.0016 ether
    );

    derivativeToken = _addPendleMarket(CRVUSD_PENDLE_28MAR_2024, "name", "symbol", MAX_CARDINALITY);

    pendleChildLpOracleInstance = new PendleChildLpOracle(address(pendleLpOracleInstance), address(derivativeToken));

    underlyingTokens = new address[](1);
    underlyingTokens[0] = underlyingFeed;

    wiseOracleHubInstance.addOracle(
        address(derivativeToken), IPriceFeed(address(pendleChildLpOracleInstance)), underlyingTokens
    );

    PoolManager.CreatePool[] memory createPoolArray = new PoolManager.CreatePool[](3);

    createPoolArray[0] = PoolManager.CreatePool({
        allowBorrow: true,
        poolToken: CRVUSD_TOKEN_ADDRESS,
        poolMulFactor: 17500000000000000,
        poolCollFactor: 740000000000000000,
        maxDepositAmount: 2000000000000000000000000
    });

    createPoolArray[1] = PoolManager.CreatePool({
        allowBorrow: false,
        poolToken: controllerTester.pendleChildAddress(AddressesMap[chainId].PendleMarketStEth),
        poolMulFactor: 17500000000000000,
        poolCollFactor: 740000000000000000,
        maxDepositAmount: 2000000000000000000000000
    });

    createPoolArray[2] = PoolManager.CreatePool({
        allowBorrow: false,
        poolToken: controllerTester.pendleChildAddress(CRVUSD_PENDLE_28MAR_2024),
        poolMulFactor: 17500000000000000,
        poolCollFactor: 740000000000000000,
        maxDepositAmount: 2000000000000000000000000
    });

    for (uint256 i = 0; i < createPoolArray.length; i++) {
        wiseLendingInstance.createPool(createPoolArray[i]);
    }

    powerFarmNftsInstance = new PowerFarmNFTs("", "");

    powerFarmManagerInstance = new PendlePowerManager(
        address(wiseLendingInstance),
        controllerTester.pendleChildAddress(AddressesMap[chainId].PendleMarketStEth),
        _pendleRouter,
        AddressesMap[chainId].entryAssetPendleMarketStEth,
        AddressesMap[chainId].PendleMarketStEthSy,
        AddressesMap[chainId].PendleMarketStEth,
        AddressesMap[chainId].pendleRouterStatic,
        AddressesMap[chainId].dex,
        950000000000000000,
        address(powerFarmNftsInstance)
    );

    wiseLendingInstance.setVerifiedIsolationPool(address(powerFarmManagerInstance), true);

    vm.stopPrank();

    if (block.chainid == ETH_CHAIN_ID) {
        address wethWhaleEthMain = 0x8EB8a3b98659Cce290402893d0123abb75E3ab28;

        vm.startPrank(wethWhaleEthMain);

        wethInstance.transfer(wiseLendingInstance.master(), 1000 ether);

        vm.stopPrank();
    }

    vm.startPrank(wiseLendingInstance.master());

    IERC20(AddressesMap[chainId].weth).approve(address(powerFarmManagerInstance), 1000000 ether);

    wiseSecurityInstance = IWiseSecurity(wiseLendingInstance.WISE_SECURITY());

    positionNftsInstance = IPositionNFTs(wiseLendingInstance.POSITION_NFT());
}

function testCompatibleWithRouter() public {
    address pendleRouter = 0x0000000001E4ef00d069e71d6bA041b0A16F7eA0;
    _decideChain(true);
    _setUpCustom(pendleRouter);
    _testFarmShouldEnterAndExitIntoToken();
}

function testFail_IncompatibleWithRouterV3() public {
    address pendleRouterV3 = 0x00000000005BBB0EF59571E58418F9a4357b68A0;
    _decideChain(true);
    _setUpCustom(pendleRouterV3);
    // Reverts with "RouterInvalidAction"
    _testFarmShouldEnterAndExitIntoToken();
}
```

## Tools Used

Manual Review

## Recommended Mitigation Steps

Support only the latest router (V3) or add conditional checks to use the respective selector for each router version.



## Assessed type

Other
